from rest_framework import status, viewsets
from .models import User, Business, Employee, Customer, Inventory, InventoryItem, Appointment, Appeal, Notification, Service, Review

from . import serializers

from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly,  IsEmployee, \
    IsEmployeeOrReadOnly, IsEmployeeOrCustomerOrReadOnly, \
    IsAdminUserOrReadOnly, IsBusinessOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django_filters import rest_framework as django_filters
from django.core.exceptions import PermissionDenied

from .paginations import MyPagination


from django.db.models import Q


class UserViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )

    # [{only my user }]
    # def get_queryset(self):
    # return self.queryset.filter(user=self.request.user)
    # return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = self.get_serializer(instance=user, many=False)
        return Response(serializer.data)

    def has_role(self, user):
        return hasattr(user, 'business') or hasattr(user, 'employee') or hasattr(user, 'customer')

    @action(detail=True, methods=['post'])
    def set_role(self, request, pk=True):
        user = self.get_object()
        if request.user != user:
            return Response({"user": "Permission denied"}, status=status.HTTP_400_BAD_REQUEST)
        if self.has_role(user):
            return Response({"user": "This user already has a role"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        # get url
        serializer = self.serializer_class(user, context={'request': request})
        url = serializer.data['url']
        data["user"] = url

        # serialize
        if request.role == 'employee':
            # check business field
            if not 'business' in data:
                data['business'] = None
            serializer = serializers.EmployeeSerializer(data = data)
        elif request.role == 'business':
            serializer = serializers.BusinessSerializer(data = data)
        elif request.role == 'customer':
            serializer = serializers.CustomerSerializer(data = data)
        else:
            return Response({"detail": "Wrong role provided"},
                status=status.HTTP_400_BAD_REQUEST)

        # check if valid
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        # ok
        data = serializer.validated_data
        if request.role == 'employee':
            Employee.objects.create(first_name=data['first_name'], last_name=data['last_name'], user=user, business=data['business'])
        elif request.role == 'business':
            Business.objects.create(title=data['title'], user=user)
        elif request.role == 'customer':
            Customer.objects.create(first_name=data['first_name'], last_name=data['last_name'], user=user)

        return Response({"detail": "You're {} now!".format(request.role)})


class BusinessViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Business.objects.all()
    serializer_class = serializers.BusinessSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,)

    # read only
    def get_queryset(self):
        # TODO
        return self.queryset.all()

    @action(detail=True, methods=['get'], pagination_class=MyPagination)
    def services(self, request, pk=None):
        current_business = self.get_object()
        search_query = request.GET.get('search')

        title_filter = request.GET.get('title')

        queryset = Service.objects.filter(business=current_business)

        if search_query:
            queryset = queryset.filter(Q(title__contains=search_query))
        elif title_filter:
            queryset = queryset.filter(Q(title=title_filter))

        queryset = queryset.order_by('-updated_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ServiceSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.ServiceSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Employee.objects.all().order_by('-updated_at')
    serializer_class = serializers.EmployeeSerializer

    permission_classes = (IsAuthenticated , IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('user__first_name', 'user__last_name')
    filter_fields = ('user__first_name', 'user__last_name')

    # read only
    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "employee":
            # employee can see himself and employees from his business
            employee_business = getattr(self.request.user.employee, 'business', False)
            employee_uid = getattr(self.request.user.employee, 'uid', None)
            if employee_business:
                return self.queryset.filter(Q(uid=employee_uid) | Q(businesses__id=employee_business.id))
            else:
                return self.queryset.filter(uid=employee_uid)
        elif role == "customer":
            return self.queryset.all()
        elif role == "business":
            # business can see employee from current business
            # return self.queryset.filter(business=self.request.user.business)
            return self.queryset.filter(businesses__id=self.request.user.business.id)
        else:
            raise PermissionDenied()

class CustomerViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Customer.objects.all().order_by('-updated_at')
    #queryset = self.filter_queryset(self.get_queryset()).filter()

    serializer_class = serializers.CustomerSerializer
    permission_classes = (IsAuthenticated , IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('first_name', 'uid', 'last_name')
    filter_fields = ('first_name', 'uid', 'last_name')

    # read only
    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "employee":
            # employee can see his customers
            # TODO: Do not serialize customer.employee
            return self.queryset.filter(employees=self.request.user.employee)
        elif role == "customer":
            # customer can see only himself
            return self.queryset.filter(uid=self.request.user.customer.uid)
        elif role == "business":
            # business can see customers with employee from current business
            return self.queryset.filter(owner=self.request.user.business)
        else:
            raise PermissionDenied()

    def retrieve(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(customer, context={'request': request})
        return Response(serializer.data)


    # create only for employee.
    def perform_create(self, serializer):
        employee = getattr(self.request.user, 'employee', False)
        business = getattr(self.request.user, 'business', False)
        if employee:
            serializer.save(owner=employee.business)
        elif business:
            serializer.save(owner=business)
        else:
            raise PermissionDenied()


    # # TODO: perform update
    # @action(detail=True, methods=['post'])
    # def remove_employee(self, request, pk=None):
    #     employee_id = request.data.get('employee_id')
    #     if not employee_id:
    #         return Response({"employee_id": "Provide employee id"}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     current_customer = self.get_object()
    #     if not current_customer:
    #         return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)
    #
    #     user_user = self.request.user
    #     print(user_user.role)
    #     if user_user.role != "employee" and user_user.role != "customer":
    #         raise PermissionDenied()
    #     print('here')
    #     if user_user.role == "employee" and employee_id != user_user.employee.id:
    #         raise PermissionDenied()
    #     if user_user.role == "customer" and current_customer.id != user_user.customer.id:
    #         raise PermissionDenied()
    #     # check if customer has employees
    #     if not current_customer.employees.exists():
    #         return Response({"detail": "Customer has no employees"}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # get employee
    #     try:
    #         employee = current_customer.employees.get(pk=employee_id)
    #     except Employee.DoesNotExist:
    #         return Response({'employee_id': 'Not found employee with id {} in customer {} employees set'.format(employee_id, current_customer.id)}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # remove from customer.employees employee with employee_id
    #     current_customer.employees.remove(employee)
    #     current_customer.save()
    #
    #     # return = customer
    #     serializer = CustomerSerializer(current_customer, context={'request': request})
    #     return Response(serializer.data)


    # @action(detail=True, methods=['get'], pagination_class=MyPagination)
    # def employees(self, request, pk=None):
    #     search_query = request.GET.get('search')
    #
    #     uid_filter = request.GET.get('uid')
    #     first_name_filter = request.GET.get('first_name')
    #     last_name_filter = request.GET.get('last_name')
    #
    #     current_customer = self.get_object()
    #     queryset = current_customer.employees
    #
    #     if search_query:
    #         queryset = queryset.filter( \
    #                              Q(uid=search_query) \
    #                            | Q(first_name__icontains=search_query) \
    #                            | Q(last_name__icontains=search_query))
    #     elif uid_filter or first_name_filter or last_name_filter:
    #         queryset = queryset.filter( \
    #                              Q(uid=uid_filter) \
    #                            | Q(first_name=first_name_filter) \
    #                            | Q(last_name=last_name_filter))
    #
    #     queryset = queryset.order_by('-updated_at')
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = EmployeeSerializer(page, many=True, context={'request': request})
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = EmployeeSerializer(queryset, many=True, context={'request': request})
    #
    #     return Response(serializer.data)
    #

    @action(detail=False, methods=['get'], pagination_class=MyPagination)
    def all(self, request):
        search_query = request.GET.get('search')

        uid_filter = request.GET.get('uid')
        first_name_filter = request.GET.get('first_name')
        last_name_filter = request.GET.get('last_name')

        queryset = Customer.objects.all()

        if search_query:
            queryset = queryset.filter( \
                                 Q(uid=search_query) \
                               | Q(first_name__icontains=search_query) \
                               | Q(last_name__icontains=search_query))
        elif uid_filter or first_name_filter or last_name_filter:
            queryset = queryset.filter( \
                                 Q(uid=uid_filter) \
                               | Q(first_name=first_name_filter) \
                               | Q(last_name=last_name_filter))

        queryset = queryset.order_by('-updated_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.CustomerSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.CustomerSerializer(queryset, many=True, context={'request': request})

        return Response(serializer.data)

# class DataViewSet(viewsets.ModelViewSet):
#     """
#     """
#     queryset = Data.objects.all().order_by('-updated_at')
#     serializer_class = serializers.DataSerializer
#     permission_classes = (IsAuthenticated,  IsOwnerOrReadOnly, )# IsEmployeeOrCustomerOrReadOnly, )
#     filter_backends = (filters.SearchFilter, DjangoFilterBackend)
#     search_fields = ('customer__first_name', 'customer__last_name', 'data')
#     filter_fields = ('customer__id', 'data', 'is_public' )
#
#     # read only
#     def get_queryset(self):
#         role = getattr(self.request.user, 'role', False)
#         if role == "employee":
#             # employee can see his customers
#             return self.queryset.filter(employee=self.request.user.employee)
#         elif role == "customer":
#             # customer can see only himself
#             return self.queryset.filter(customer=self.request.user.customer)
#         elif role == "business":
#             # business can see customers with employee from current business
#             return self.queryset.filter(employee__business=self.request.user.business)
#         else:
#             raise PermissionDenied()
#
#     # create only for employee & customer.
#     def perform_create(self, serializer):
#         role = getattr(self.request.user, 'role', False)
#         if role == "employee":
#             employee = self.request.user.employee
#             serializer.save(employee=employee)
#         elif role == "customer":
#             # optional employee
#             customer = self.request.user.customer
#             serializer.save(customer=customer)
#         else:
#             raise PermissionDenied()
#
#     # /data-url/last/:customer_id
#     @action(detail=False, methods=['get'], url_path='last/(?P<customer_id>[^/.]+)')
#     def last(self, request, customer_id):
#
#         queryset = self.get_queryset().filter(customer__id=customer_id)
#
#         queryset = queryset.order_by('-created_at')
#         last_data = queryset.first()
#
#         if last_data:
#             serializer = DataSerializer(last_data, many=False, context={'request': request})
#             return Response(serializer.data)
#
#         return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)
# class RecipeViewSet(viewsets.ModelViewSet):
#     """
#     """
#     queryset = Recipe.objects.all().order_by('-updated_at')
#     serializer_class = serializers.RecipeSerializer
#     permission_classes = (IsAuthenticated,  IsOwnerOrReadOnly, )
#     filter_backends = (filters.SearchFilter, DjangoFilterBackend)
#     search_fields = ('customer__first_name', 'customer__last_name', 'reviews', 'diagnosis')
#     filter_fields = ('customer__id', 'employee__id', 'is_public' )
#
#     # read only
#     def get_queryset(self):
#         role = getattr(self.request.user, 'role', False)
#         if role == "employee":
#             # employee can see his customers
#             return self.queryset.filter(employee=self.request.user.employee)
#         elif role == "customer":
#             # customer can see only himself
#             return self.queryset.filter(customer=self.request.user.customer)
#         elif role == "business":
#             # business can see customers with employee from current business
#             return self.queryset.filter(employee__business=self.request.user.business)
#         else:
#             raise PermissionDenied()
#
#     # create only for employee
#     def perform_create(self, serializer):
#         role = getattr(self.request.user, 'role', False)
#         if role == "employee":
#             employee = self.request.user.employee
#             serializer.save(employee=employee)
#         else:
#             raise PermissionDenied()

class AppealViewSet(viewsets.ModelViewSet):
    """
    Appeals view set
    (request from employee to business, from employee to customer,
     from customer to business to connect them)
    """
    queryset = Appeal.objects.all().order_by('-updated_at')
    serializer_class = serializers.AppealSerializer
    permission_classes = (IsAuthenticated,  IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('title', 'text')
    filter_fields = ('author__id', 'recipient__id', 'author', 'recipient', 'answered', 'accepted')

    """
    NOTE: filters income and outcome actions too
    """
    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role:
            if self.action == 'income':
                return self.queryset.filter(recipient=self.request.user)
            elif self.action == 'outcome':
                return self.queryset.filter(author=self.request.user)
            else:
                return self.queryset.filter( \
                                        Q(author=self.request.user) | \
                                        Q(recipient=self.request.user) )
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        role = getattr(self.request.user, 'role', False)
        if not role:
            raise PermissionDenied()

        if serializer.is_valid(raise_exception=True):
            author = self.request.user
            current_request = serializer.save(author=author)

            notification = Notification()
            notification.title = "New request"
            notification.text = current_request.title
            notification.recipient = current_request.recipient
            notification.redirect_url = '/requests/{}'.format(current_request.id)
            # default notification datetime
            notification.save()

    """
    filtering:
        author__id
    """
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly,])
    def income(self, request):
        queryset = self.get_queryset()
        author_id = request.GET.get('author__id')
        answered = request.GET.get('answered')

        if author_id:
            queryset = queryset.filter(author=author_id)
        if answered != None:
            queryset = queryset.filter(answered=answered)

        queryset = queryset.order_by('-updated_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.AppealSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.AppealSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    """
    filtering:
        recipient__id
    """
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly,])
    def outcome(self, request):
        queryset = self.get_queryset()
        recipient_id = request.GET.get('recipient__id')
        answered = request.GET.get('answered')

        if recipient_id:
            queryset = queryset.filter(recipient=recipient_id)
        if answered != None:
            queryset = queryset.filter(answered=answered)

        queryset = queryset.order_by('-updated_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.AppealSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = serializers.AppealSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    """
    Accepting request
    """
    def process_accepted_request(self, current_request):
        author = current_request.author
        recipient = current_request.recipient
        # serializer validated before

        if author.role == 'employee':
            # from employee
            #if reipient.role == 'customer':
                # to customer (ask customer if he wants author to be his employee, customer accepted)
                # customer wants to add employee to his employees list
                # recipient.customer.set_owner(author.employee.business)
            if recipient.role == 'business':
                # to business (author asks to be registered in business, business accepted)
                employee = author.employee
                employee.add_business(recipient.business)
        # elif author.role == 'customer':
            # from customer
            # if recipient.role == 'business':
            #     author.customer.add_employee(recipient.employee)
        elif author.role == 'business':
            # from business
            if recipient.role == 'employee':
                # to employee (ask employee if he wants to be in business)
                employee = recipient.employee
                employee.add_business(author.business)

        return Response({"accepted": True})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly, ])
    def accept(self, request, pk=True):
        current_request = self.get_object()

        serializer = serializers.AppealSerializer(data = current_request, context={'request': request})
        serializer.is_valid()
        serializer.validate_on_answering()
        serializer.validate_on_accepting()
        #
        # current_request.accepted = True
        # current_request.answered = True
        result = self.process_accepted_request(current_request)
        # current_request.save()
        current_request.delete()
        return result

    """
    Rejecting request
    """
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly, ])
    def reject(self, request, pk=True):
        current_request = self.get_object()

        serializer = serializers.AppealSerializer(data = current_request, context={'request': request})
        serializer.validate_on_answering()

        # current_request.accepted = False
        # current_request.answered = True
        # current_request.save()
        current_request.delete()
        return Response({"accepted": False})


class ServiceViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Service.objects.all()
    serializer_class = serializers.ServiceSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, IsBusinessOrReadOnly)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('title', 'description')

    # create only for employee & customer.
    def perform_create(self, serializer):
        role = getattr(self.request.user, 'role', False)
        if role == "business":
            b = self.request.user.business
            serializer.save(business=b)
        else:
            raise PermissionDenied()

    # read only
    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "business":
            return self.queryset.filter(business=self.request.user.business)
        else:
            raise PermissionDenied()
"""
Appointments
"""
# appointments filter by datetime ISO range
# i.e
# /appointments/?start_datetime_before=2019-02-09T21:00:00Z&start_datetime_after=2019-02-09T20:00:00Z
class AppointmentFilter(django_filters.FilterSet):
    start_datetime = django_filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = Appointment
        fields = ['start_datetime','customer__id', 'title', 'is_public', 'employee__id',
                  'start_datetime', ]


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Appointment.objects.all().order_by('-updated_at')
    serializer_class = serializers.AppointmentSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly,  ) #IsEmployeeOrCustomerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('customer__first_name', 'customer__last_name', 'title')
    # filter_fields = ()
    filterset_class = AppointmentFilter

    # read only
    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "employee":
            # employee can see his customers
            return self.queryset.filter(employee=self.request.user.employee)
        elif role == "customer":
            # customer can see only himself
            return self.queryset.filter(customer=self.request.user.customer)
        elif role == "business":
            # business can see customers with employee from current business
            return self.queryset.filter(business=self.request.user.business)
        else:
            raise PermissionDenied()

    # create only for employee & customer.
    def perform_create(self, serializer):
        role = getattr(self.request.user, 'role', False)
        if role == "employee":
            employee = self.request.user.employee
            serializer.save(employee=employee)
        elif role == "business":
            business = self.request.user.business
            serializer.save(business=business)
        elif role == "customer":
            customer = self.request.user.customer
            serializer.save(customer=customer)
        else:
            raise PermissionDenied()



class NotificationViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('recipient__first_name', 'recipient__last_name', 'title', 'text')
    # filter_fields = ('recipient__id')

    # read only
    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('title', 'text')
    filter_fields = ('recipient__id', 'author__id', 'service__id')

    # read only
    # def get_queryset(self):
    #     return self.queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class InventoryViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Inventory.objects.all()
    serializer_class = serializers.InventorySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('title')
    filter_fields = ('business__id', )

    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "business":
            return self.queryset.filter(business=self.request.user.business)
        elif role == "employee":
            return self.queryset.filter(business__in=self.request.user.employee.businesses.all())
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        role = getattr(self.request.user, 'role', False)
        if role == "business":
            serializer.save(business=self.request.user.business)
        else:
            raise PermissionDenied()

class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    TODO:
    """
    queryset = InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('title', 'details')
    filter_fields = ('inventory__id', 'uuid')

    def get_queryset(self):
        role = getattr(self.request.user, 'role', False)
        if role == "business":
            return self.queryset.filter(inventory__business=self.request.user.business)
        elif role == "employee":
            return self.queryset.filter(inventory__business__in=self.request.user.employee.businesses.all())
        else:
            raise PermissionDenied()

