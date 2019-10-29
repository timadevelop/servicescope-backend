from django.conf import settings
from django.utils import timezone
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.targetingsearch import TargetingSearch
from facebook_business.adobjects.targeting import Targeting
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.pagepost import PagePost


FacebookAdsApi.init(settings.FACEBOOK_APP_ID,
                    settings.FACEBOOK_APP_SECRET, settings.FACEBOOK_ACCESS_TOKEN)

AD_ACCOUNT_ID = 'act_{}'.format(settings.FACEBOOK_AD_ACCOUNT_ID)

"""

Related articles:
https://developers.facebook.com/docs/marketing-api/campaign-structure
https://developers.facebook.com/docs/marketing-api/buying-api
https://developers.facebook.com/docs/marketing-api/buying-api/ad-units/
https://github.com/facebook/facebook-python-business-sdk/blob/15c8b3e453f6115d029a2b5270c710d04e1c1c81/examples/MultiPromoteYourPage.py

"""
class FacebookAdsManager:
    account = AdAccount(AD_ACCOUNT_ID)

    """
    Gets all campaigns for current account
    @returns [ {id: <campaign_id>}, {id: ....}, .... ]
    """
    def get_campaigns(self):
        campaigns_cursor = self.account.get_campaigns()
        return [doc for doc in campaigns_cursor]

    """
    Creates campaign
    @returns {id: <new_campaign_id>}
    """
    def create_campaign(self):
        fields = []
        params = {
            'name': 'My new campaign',
            'objective': 'LINK_CLICKS',
            'status': 'PAUSED',
        }
        result = self.account.create_campaign(fields=fields,params=params)
        ad_campaign_id = result.get_id()
        return result


    """
    Searches targeting interests
    @returns [
        {
            id: <targeting_id>,
            name: <targeting_name>,
            audience_size: <number>,
            path: [string],
            description?: null,
            disambiguation_category: string (like 'Product/Service'),
            topic: string
        }
    ]
    """
    def search_targeting_interests(self, query):
        params = {
            'q': query,
            'type': 'adinterest',
        }

        interests = TargetingSearch.search(params=params)
        return interests

    """
    Generates targeting spec by query like "cars"
    TODO: optimize
    """
    def generate_targeting_spec(self, interests_query):
        def normalize(interest):
            return interest.get("id")
        targeting = {
            Targeting.Field.geo_locations: {
                Targeting.Field.countries: ['BG'],
            },
            Targeting.Field.interests: ["6004353319322", "6003056834444"],
        }
        return targeting

    """
    Create a new Ad Set
    """
    def create_ad_set(self, campaign_id, budget, targeting_query):
        today = timezone.datetime.today()
        start_time = str(today + timezone.timedelta(weeks=1))
        end_time = str(today + timezone.timedelta(weeks=2))

        targeting = self.generate_targeting_spec(targeting_query)
        print(targeting)
        # new AdSet instance
        adset = AdSet(parent_id=AD_ACCOUNT_ID)
        adset.update({
            AdSet.Field.name: 'My New Ad Set',
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.daily_budget: budget,
            AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
            AdSet.Field.optimization_goal: AdSet.OptimizationGoal.reach,
            AdSet.Field.bid_amount: 2,
            AdSet.Field.targeting: targeting,
            AdSet.Field.start_time: start_time,
            AdSet.Field.end_time: end_time,
        })

        result = adset.remote_create(params={
            'status': AdSet.Status.paused,
        })
        # print(result)
        return result
    """
    Get Ad Sets
    @returns [
        {
            id: <adset_id>,
            name: <adset_name>
        }
    ]
    """
    def get_ad_sets(self):
        return [adset for adset in self.account.get_ad_sets(fields=[AdSet.Field.name, AdSet.Field.id])]

    """
    Advertise facebook page post
    """
    def advertise_post(self, post_id, adset_id):
        def create_ad_creative(name):
            # see https://github.com/facebook/facebook-python-business-sdk/blob/2c6ea98825ff293c0fb33738fa7322dcef9e2e07/examples/AdAccountAdCreativesPost.py#L35
            # returs AdCreative instance
            fields = [
            ]
            params = {
                'name': name,
                'object_story_id': '{}'.format(post_id)
            }
            return self.account.create_ad_creative(fields=fields,params=params)
        def create_ad(name, creative_id, status):
            fields = [
            ]
            params = {
                'name': name,
                'adset_id': adset_id,
                'creative': {'creative_id': creative_id},
                'status': status,
            }
            return self.account.create_ad(fields=fields, params=params)

        ad_creative = create_ad_creative('Sample Post Ad Creative for post#{}'.format(post_id))
        created_ad = create_ad('Sample Ad for post#{}'.format(post_id), ad_creative.get_id(), 'PAUSED')
        return created_ad

    """
    Create a new facebook page post
    """
    def create_post(self, message):
        fields = [
        ]
        params = {
            'message': message
        }
        post = Page(settings.FACEBOOK_PAGE_ID).create_feed(
            fields=fields,
            params=params,
        )
        post_id = post.get_id()
        return post_id

    """
    Delete facebook page post by id
    Example: .delete_post("435524993668529_511529099401451")
    """
    def delete_post(self, post_id):
        fields = []
        params = {}
        return PagePost(post_id).api_delete(fields=fields,params=params)

facebookAdsManager = FacebookAdsManager()
