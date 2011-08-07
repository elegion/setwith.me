# -*- coding: utf-8 -*-
import urllib
import urllib2

import facebook


def get_access_token(application_id, application_secret, code, redirect_url):
    """
    Get the access_token for the user with code, provided by facebook
    application_id = retrieved from the developer page
    application_secret = retrieved from the developer page
    code = provided by facebook in GET after auth dialog
    redirect url = required by facebook for some reason
    returns the access_token
    """
    # Get user access token
    args = {'code': code,
            'client_id': application_id,
            'client_secret': application_secret,
            'redirect_uri': redirect_url}

    try:
        result_io = urllib2.urlopen(
            "https://graph.facebook.com/oauth/access_token?" +
            urllib.urlencode(args))
    except urllib2.HTTPError as error:
        if 'www-authenticate' in error.headers:
            raise facebook.GraphAPIError(
                'AccessToken',
                error.headers['www-authenticate'])
        else:
            raise

    try:
        access_token, expires = result_io.read().split('&')
    finally:
        result_io.close()

    return access_token.split('=')[1], expires.split('=')[1]


def get_app_access_token(application_id, application_secret):
    """
    Get the access_token for the app that can be used for
        insights and creating test users
    application_id = retrieved from the developer page
    application_secret = retrieved from the developer page
    returns the application access_token
    """
    # Get an app access token
    args = {'grant_type': 'client_credentials',
            'client_id': application_id,
            'client_secret': application_secret}

    try:
        result_io = urllib2.urlopen(
            "https://graph.facebook.com/oauth/access_token?" +
            urllib.urlencode(args))
    except urllib2.HTTPError as error:
        if 'www-authenticate' in error.headers:
            raise facebook.GraphAPIError(
                'AccessToken',
                error.headers['www-authenticate'])
        else:
            raise

    try:
        result = result_io.read().split("=")[1]
    finally:
        result_io.close()

    return result


def parse_graph_error(header_content):
    prefix = 'OAuth "Facebook Platform" '
    text_split = '" "'
    code_prefix = '(#'
    code_split = ') '
    if not header_content.startswith(prefix):
        return None
    text = header_content.lstrip(prefix).strip('"')
    text_lst = text.split(text_split)
    if len(text_lst) != 2:
        return None
    er_type, er_text = text_lst[0], text_lst[1]
    if not er_text.startswith(code_prefix):
        return None
    er_text = er_text.lstrip(code_prefix)
    er_lst = er_text.split(code_split)
    if len(er_lst) != 2:
        return None
    return er_lst[0], er_lst[1]


def handle_error(http_error):
    if 'www-authenticate' in http_error.headers:
        code_detail = parse_graph_error(
            http_error.headers['www-authenticate'])
        if code_detail:
            code = code_detail[0]
            msg = code_detail[1]
        else:
            code = 'GenericGraphError'
            msg = http_error.headers['www-authenticate']
        raise facebook.GraphAPIError(code, msg)
    else:
        raise


class GraphAPI(facebook.GraphAPI):

    def request(self, path, args=None, post_args=None):
        try:
            return super(GraphAPI, self).request(path, args, post_args)
        except urllib2.HTTPError as error:
            handle_error(error)

    def api_request(self, path, args=None, post_args=None):
        try:
            return super(GraphAPI, self).api_request(path, args, post_args)
        except urllib2.HTTPError as error:
            handle_error(error)

    def fql(self, query, args=None, post_args=None):
        try:
            return super(GraphAPI, self).fql(query, args, post_args)
        except urllib2.HTTPError as error:
            handle_error(error)
