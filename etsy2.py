from __future__ import division
import requests
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1
import json
from datetime import datetime, timedelta
import time


class Etsy():
    carriers = {
        "fedex": "fedex", 
        "fedex uk (domestic)": "fedex-uk",
        "ups": "ups",
        "ups freight": "ups-freight",
        "usps": "usps"
        }
    base_url = "https://openapi.etsy.com/v2/"


    def __init__(self, key_string=None, shared_secret=None, shop_id=None, owner_key=None, owner_secret=None):
        """
        """
        self.key_string = key_string
        self.shared_secret = shared_secret
        self.shop_id = shop_id
        self.owner_key = owner_key
        self.owner_secret = owner_secret


    ##############################################
    ############### CONNECT OAUTH ################
    ##############################################

    def get_oauth_verifier(self, permission_scope=[]):
        '''
        https://www.etsy.com/developers/documentation/getting_started/oauth
        possible permissions
        '''
        permission_scope = ' '.join(permission_scope)
        full_url = '{}oauth/request_token?scope={}'.format(self.base_url, permission_scope)
        oauth = OAuth1Session(self.key_string, client_secret=self.shared_secret)
        fetch_response = oauth.fetch_request_token(full_url)
        owner_key = fetch_response.get("oauth_token")
        owner_secret = fetch_response.get("oauth_token_secret")
        login_url = fetch_response.get("login_url")
        return {'login_url': login_url, 'owner_key': owner_key, 'owner_secret': owner_secret}

    def verify_oauth(self, owner_key, owner_secret, verifier):
        '''
        use after using get_oauth_verifier to get OAuth certification
        '''
        access_token_url = "{}oauth/access_token".format(self.base_url)
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=owner_key,
            resource_owner_secret=owner_secret,
            verifier=verifier
            )
        oauth_tokens = oauth.fetch_access_token(access_token_url)
        resource_owner_key = oauth_tokens.get("oauth_token")
        resource_owner_secret = oauth_tokens.get("oauth_token_secret")
        owner_key = resource_owner_key
        owner_secret = resource_owner_secret
        return {'owner_key': owner_key, 'owner_secret': owner_secret}

    ##################################################
    ################### LISTINGS #####################
    ##################################################

    def find_all_shop_listings_active(
            self,
            limit=50,
            offset=0,
            page=None,
            shop_id=None,
            keywords=[],
            sort_on=None,                   # created, price, score
            sort_order=None,                # down, up
            min_price=None,
            max_price=None,
            color=None,
            color_accuracy=None,
            tags=[],
            category=None,
            translate_keywords=None,        # true, false
            include_private=None,
            timeout=None
            ):
        '''
        '''
        if not shop_id:
            shop_id = self.shop_id
        full_url = '{}shops/{}/listings/active'.format(self.base_url, shop_id)
        params = {'api_key': self.key_string}
        if limit: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if page: params['page'] = page
        if keywords:
            keywords = ','.join(keywords)
            params['keywords'] = keywords
        if sort_on: params['sort_on'] = sort_on
        if sort_order: params['sort_order'] = sort_order
        if min_price: params['min_price'] = min_price
        if max_price: params['max_price'] = max_price
        if color: params['color'] = color
        if color_accuracy: params['color_accuracy'] = color_accuracy
        if tags:
            tags = ','.join(tags)
            params['tags'] = tags
        if category: params['category'] = category
        if translate_keywords: params['translate_keywords'] = translate_keywords
        if include_private: params['include_private'] = include_private
        r = requests.get(full_url, params=params, timeout=timeout)
        return r

    def find_all_shop_listings_inactive(
            self,
            limit=50,
            offset=0,
            page=None,
            shop_id=None,
            timeout=None
            ):
        '''
        '''
        if not shop_id:
            shop_id = self.shop_id
        full_url = '{}shops/{}/listings/active'.format(self.base_url, shop_id)
        params = {}
        if limit: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if page: params['page'] = page
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.get(full_url, params=params, timeout=timeout)
        return r

    def update_listing(
            self,
            listing_id,
            quantity=None,
            title=None,
            description=None,
            price=None,
            wholesale_price=None,
            materials=[],
            renew=None,                 # true | false
            shipping_template_id=None,
            shop_section_id=None,
            state=None,                 # enum(active, inactive, draft)
            image_ids=[],
            is_customizable=None,
            item_weight=None,
            item_length=None,
            item_width=None,
            item_height=None,
            item_weight_unit=None,
            item_dimensions_unit=None,
            non_taxable=None,
            category_id=None,
            taxonomy_id=None,
            tags=[],
            who_made=None,              # enum(i_did, collective, someone_else)
            is_supply=None,
            when_made=None,             # enum(made_to_order, 2010_2017, 2000_2009, 1998_1999, before_1998, 1990_1997, 1980s, 1970s, 1960s, 1950s, 1940s, 1930s, 1920s, 1910s, 1900s, 1800s, 1700s, before_1700)
            recipient=None,             # enum(men, women, unisex_adults, teen_boys, teen_girls, teens, boys, girls, children, baby_boys, baby_girls, babies, birds, cats, dogs, pets, not_specified)
            occasion=None,              # enum(anniversary, baptism, bar_or_bat_mitzvah, birthday, canada_day, chinese_new_year, cinco_de_mayo, confirmation, christmas, day_of_the_dead, easter, eid, engagement, fathers_day, get_well, graduation, halloween, hanukkah, housewarming, kwanzaa, prom, july_4th, mothers_day, new_baby, new_years, quinceanera, retirement, st_patricks_day, sweet_16, sympathy, thanksgiving, valentines, wedding)
            style=[],
            processing_min=None,
            processing_max=None,
            featured_rank=None,
            timeout=None
            ):
        '''
        https://www.etsy.com/developers/documentation/reference/listing#method_updatelisting
        requires "listing_w" authorization
        '''
        full_url = '{}listings/{}'.format(self.base_url, listing_id)
        params = {}
        if quantity is not None: params['quantity'] = quantity
        if title is not None: params['title'] = title
        if description is not None: params['description'] = description
        if price is not None: params['price'] = price
        if wholesale_price is not None: params['wholesale_price'] = wholesale_price
        if materials:
            materials = ','.join(materials)
            params['materials'] = materials
        if renew is not None: params['renew'] = renew
        if shipping_template_id is not None: params['shipping_template_id'] = shipping_template_id
        if shop_section_id is not None: params['shop_section_id'] = shop_section_id
        if state is not None: params['state'] = state
        if image_ids:
            image_ids = ','.join(image_ids)
            params['image_ids'] = image_ids
        if is_customizable is not None: params['is_customizable'] = is_customizable
        if item_weight is not None: params['item_weight'] = item_weight
        if item_length is not None: params['item_length'] = item_length
        if item_width is not None: params['item_width'] = item_width
        if item_height is not None: params['item_height'] = item_height
        if item_weight_unit is not None: params['item_weight_unit'] = item_weight_unit
        if item_dimensions_unit is not None: params['item_dimensions_unit'] = item_dimensions_unit
        if non_taxable is not None: params['non_taxable'] = non_taxable
        if category_id is not None: params['category_id'] = category_id
        if taxonomy_id is not None: params['taxonomy_id'] = taxonomy_id
        if tags:
            tags = ','.join(tags)
            params['tags'] = tags
        if who_made is not None: params['who_made'] = who_made
        if is_supply is not None: params['is_supply'] = is_supply
        if when_made is not None: params['when_made'] = when_made
        if recipient is not None: params['recipient'] = recipient
        if occasion is not None: params['occasion'] = occasion
        if style:
            style = ','.join(style)
            params['style'] = style
        if processing_min is not None: params['processing_min'] = processing_min
        if processing_max is not None: params['processing_max'] = processing_max
        if featured_rank is not None: params['featured_rank'] = featured_rank
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.put(url, params=params, timeout=timeout)
        return r

    def get_listing(self, listing_id, timeout=None):
        '''
        '''
        full_url = '{}listings/{}'.format(self.base_url, listing_id)
        params = {'api_key': self.key_string}
        r = requests.get(full_url, params=params, timeout=timeout)
        return r

    def delete_listing(self, listing_id, timeout=None):
        '''
        '''
        full_url = '{}listings/{}'.format(self.base_url, listing_id)
        params = {'api_key': self.key_string}
        r = requests.delete(full_url, params=params, timeout=timeout)
        return r

    #####################################################
    ################### RECEIPTS ########################
    #####################################################

    def find_all_shop_receipts(
            self,
            shop_id=None,               # shop_id
            min_created=None,           # epoch time
            max_created=None,           # epoch time
            min_last_modified=None,     # epoch time
            max_last_modified=None,     # epoch time
            limit=50,
            offset=0,
            page=None,
            was_paid=None,              # true|false
            was_shipped=None,           # true|false
            timeout=None
            ):
        '''
        https://www.etsy.com/developers/documentation/reference/receipt#method_findallshopreceipts
        OAuth -> transaction_r
        '''
        if not shop_id:
            shop_id = self.shop_id
        full_url = '{}shops/{}/receipts'.format(self.base_url, shop_id)
        params = {}
        if min_created is not None: params['min_created'] = min_created
        if max_created is not None: params['max_created'] = max_created
        if min_last_modified is not None: params['min_last_modified'] = min_last_modified
        if max_last_modified is not None: params['max_last_modified'] = max_last_modified
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if page is not None: params['page'] = page
        if was_paid is not None: params['was_paid'] = was_paid
        if was_shipped is not None: params['was_shipped'] = was_shipped
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.get(full_url, params=params, timeout=timeout)
        return r

    def submit_tracking(
            self,
            receipt_id,
            tracking_code,
            carrier_name,
            send_bcc=False,
            shop_id=None,
            timeout=None
            ):
        '''
        https://www.etsy.com/developers/documentation/reference/receipt#method_submittracking
        OAuth -> transactions_w
        '''
        if not shop_id:
            shop_id = self.shop_id
        full_url = '{}shops/{}/receipts/{}/tracking'.format(self.base_url, shop_id, receipt_id)
        params = {
            'tracking_code': tracking_code,
            'carrier_name': carrier_name
            }
        if send_bcc is not None: params['send_bcc'] = send_bcc
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.post(full_url, params=params, timeout=timeout)
        return r

    def find_all_receipt_listings(self, receipt_id, limit=50, offset=0, page=None, timeout=None):
        '''
        https://www.etsy.com/developers/documentation/reference/listing#method_findallreceiptlistings
        OAuth -> transactions_r
        This is technically under the "listings" section of the Etsy API, but it seems more fitting to put
            with the receipt methods
        '''
        full_url = '{}receipts/{}/listings'.format(self.base_url, receipt_id)
        params = {}
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if page is not None: params['page'] = page
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.get(full_url, params=params, timeout=timeout)
        return r

    ###########################################
    ############## TRANSACTIONS ###############
    ###########################################

    def find_all_shop_receipt_transactions(
            self,
            receipt_id,
            limit=50,
            offset=0,
            page=None,
            timeout=None
            ):
        '''
        https://www.etsy.com/developers/documentation/reference/transaction#method_findallshop_receipt2transactions
        '''
        full_url = '{}receipts/{}/transactions'.format(self.base_url, receipt_id)
        params = {}
        if limit is not None: params['limit'] = limit
        if offset is not None: params['offset'] = offset
        if page is not None: params['page'] = page
        oauth = OAuth1Session(
            self.key_string,
            client_secret=self.shared_secret,
            resource_owner_key=self.owner_key,
            resource_owner_secret=self.owner_secret
            )
        r = oauth.get(full_url, params=params, timeout=timeout)
        return r

    ##########################################
    ################ COUNTRY #################
    ##########################################

    def get_country(self, country_id, timeout=None):
        full_url = '{}countries/{}'.format(self.base_url, country_id)
        params = {'api_key': self.key_string}
        r = requests.get(full_url, params=params, timeout=timeout)
        return r

    def find_all_country(self, timeout=None):
        full_url = '{}countries'.format(self.base_url)
        params = {'api_key': self.key_string}
        r = requests.get(full_url, params=params, timeout=timeout)
        return r

