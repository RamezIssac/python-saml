# -*- coding: utf-8 -*-

""" OneLogin_Saml2_Authn_Request class

Copyright (c) 2014, OneLogin, Inc.
All rights reserved.

AuthNRequest class of OneLogin's Python Toolkit.

"""
from base64 import b64encode

from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class OneLogin_Saml2_Authn_Request(object):
    """

    This class handles an AuthNRequest. It builds an
    AuthNRequest object.

    """

    def __init__(self, settings, force_authn=False, is_passive=False, set_nameid_policy=True):
        """
        Constructs the AuthnRequest object.

        :param settings: OSetting data
        :type return_to: OneLogin_Saml2_Settings

        :param force_authn: Optional argument. When true the AuthNRequest will set the ForceAuthn='true'.
        :type force_authn: bool

        :param is_passive: Optional argument. When true the AuthNRequest will set the Ispassive='true'.
        :type is_passive: bool

        :param set_nameid_policy: Optional argument. When true the AuthNRequest will set a nameIdPolicy element.
        :type set_nameid_policy: bool
        """
        self.__settings = settings

        sp_data = self.__settings.get_sp_data()
        idp_data = self.__settings.get_idp_data()
        security = self.__settings.get_security_data()

        uid = OneLogin_Saml2_Utils.generate_unique_id()
        self.__id = uid
        issue_instant = OneLogin_Saml2_Utils.parse_time_to_SAML(OneLogin_Saml2_Utils.now())

        # destination = idp_data['singleSignOnService']['url']
        destination = 'https://fed.paci.gov.kw/idp/SSO.saml2'
        provider_name_str = ''
        organization_data = settings.get_organization()
        if isinstance(organization_data, dict) and organization_data:
            langs = organization_data.keys()
            if 'en-US' in langs:
                lang = 'en-US'
            else:
                lang = langs[0]
            if 'displayname' in organization_data[lang] and organization_data[lang]['displayname'] is not None:
                provider_name_str = "\n" + '    ProviderName="%s"' % organization_data[lang]['displayname']

        force_authn_str = ''
        if force_authn is True:
            force_authn_str = "\n" + '    ForceAuthn="true"'

        is_passive_str = ''
        if is_passive is True:
            is_passive_str = "\n" + '    IsPassive="true"'

        nameid_policy_str = ''
        if set_nameid_policy:
            name_id_policy_format = sp_data['NameIDFormat']
            if 'wantNameIdEncrypted' in security and security['wantNameIdEncrypted']:
                name_id_policy_format = OneLogin_Saml2_Constants.NAMEID_ENCRYPTED

            nameid_policy_str = """
    <samlp:NameIDPolicy
        Format="%s"
        AllowCreate="true" />""" % name_id_policy_format

        requested_authn_context_str = ''
        if 'requestedAuthnContext' in security.keys() and security['requestedAuthnContext'] is not False:
            authn_comparison = 'exact'
            if 'requestedAuthnContextComparison' in security.keys():
                authn_comparison = security['requestedAuthnContextComparison']

            if security['requestedAuthnContext'] is True:
                requested_authn_context_str = "\n" + """    <samlp:RequestedAuthnContext Comparison="%s">
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>""" % authn_comparison
            else:
                requested_authn_context_str = "\n" + '     <samlp:RequestedAuthnContext Comparison="%s">' % authn_comparison
                for authn_context in security['requestedAuthnContext']:
                    requested_authn_context_str += '<saml:AuthnContextClassRef>%s</saml:AuthnContextClassRef>' % authn_context
                requested_authn_context_str += '    </samlp:RequestedAuthnContext>'

        attr_consuming_service_str = ''
        if 'attributeConsumingService' in sp_data and sp_data['attributeConsumingService']:
            attr_consuming_service_str = 'AttributeConsumingServiceIndex="1"'

        certificate = "MIIDWTCCAsKgAwIBAgIJAN2rSHgfq3x/MA0GCSqGSIb3DQEBBQUAMHwxCzAJBgNVBAYTAktXMRwwGgYDVQQIExNUaGUgU1RBVEUgT0YgS1VXQUlUMQ8wDQYDVQQHEwZLdXdhaXQxJDAiBgNVBAoTG01pbmlzdHJ5IG9mIEZvcmVpZ24gQWZmYWlyczEYMBYGA1UEAxMPYWlkLm1vZmEuZ292Lmt3MB4XDTE3MDgyODA2NDQ0M1oXDTI3MDgyODA2NDQ0M1owfDELMAkGA1UEBhMCS1cxHDAaBgNVBAgTE1RoZSBTVEFURSBPRiBLVVdBSVQxDzANBgNVBAcTBkt1d2FpdDEkMCIGA1UEChMbTWluaXN0cnkgb2YgRm9yZWlnbiBBZmZhaXJzMRgwFgYDVQQDEw9haWQubW9mYS5nb3Yua3cwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBANQe0kiwithRqgLMU6jx8NG9PVrkCAVF84sL73jENoFac8ZmT398U3Gw5ZUfJlVVvfU4VyFCI7WCLbjzuFwu2McCdosa0CaG/HMDdYuDmXyOMCbyGKii5txuqlo6o35wq09hefL69i1yMIBdcMqPQLYVJVa6/loOMV++/QkEzA7xAgMBAAGjgeIwgd8wHQYDVR0OBBYEFKEdEz9D/YkpcYE6lpYvpiEy6WjgMIGvBgNVHSMEgacwgaSAFKEdEz9D/YkpcYE6lpYvpiEy6WjgoYGApH4wfDELMAkGA1UEBhMCS1cxHDAaBgNVBAgTE1RoZSBTVEFURSBPRiBLVVdBSVQxDzANBgNVBAcTBkt1d2FpdDEkMCIGA1UEChMbTWluaXN0cnkgb2YgRm9yZWlnbiBBZmZhaXJzMRgwFgYDVQQDEw9haWQubW9mYS5nb3Yua3eCCQDdq0h4H6t8fzAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA4GBAImSBs54cT0LmLJ2tQEC/vfuPcUptSnhI7OZwBMCpND669ajfMxN6YuxDH4Nf4yR1cpD+0XRbMNtrfxq8XZ/5khsjI1uBDJ2odSu+/MiBe7P5ZMdVzM0GIq1hCT9ZZ6O6056ykP8QhoLJsGw3qm+N1FiGvDTLnxwBV4p9lLES5CX"
        signature_value = 'owbA6nJRn8TMQojq27rkqMBk+z2s8Fly1F68MEMd1InH6vFpVQqvwn7NrEP7YEJnTiHH3y8vrQvpHqBYuXoJjoZpjLdmV3jlprrzjDF+ZFUeqqfUO9h8JAVPTtxwrIEj0bfzH76pCU9h+Fu0kEekQ0UjKGHUEOZbd1+W7lmcc7U='
        assertion__consumer_service_url = 'https://api.mofa2.mykuwaitnet.net/saml?acs'
        digest_value = 'Eph2yJzbGPhlVQThAl1OHWF/bmM='
        saml_issuer = 'https://api.mofa2.mykuwaitnet.net/'
        request = """<samlp:AuthnRequest ID="%(id)s" Version="2.0" IssueInstant="%(issue_instant)s" Destination="%(destination)s" ForceAuthn="false" IsPassive="false" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" AssertionConsumerServiceURL="%(assertion__consumer_service_url)s" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"><saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">%(saml_issuer)s</saml:Issuer><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" /><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1" /><Reference URI="#%(id)s"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" /><Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><InclusiveNamespaces PrefixList="#default samlp saml ds xs xsi" xmlns="http://www.w3.org/2001/10/xml-exc-c14n#" /></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1" /><DigestValue>%(digest_value)s</DigestValue></Reference></SignedInfo><SignatureValue>%(signature_value)s</SignatureValue><KeyInfo><X509Data><X509Certificate>%(certificate)s</X509Certificate></X509Data></KeyInfo></Signature><samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified" AllowCreate="true" /></samlp:AuthnRequest>""" % \
                  {
                      'id': uid,
                      'provider_name': provider_name_str,
                      'force_authn_str': force_authn_str,
                      'is_passive_str': is_passive_str,
                      'issue_instant': issue_instant,
                      'destination': destination,
                      'assertion_url': sp_data['assertionConsumerService']['url'],
                      'entity_id': sp_data['entityId'],
                      'nameid_policy_str': nameid_policy_str,
                      'requested_authn_context_str': requested_authn_context_str,
                      'attr_consuming_service_str': attr_consuming_service_str,
                      'certificate': certificate,
                      'signature_value': signature_value,
                      'digest_value': digest_value,
                      'assertion__consumer_service_url': assertion__consumer_service_url,
                      'saml_issuer':saml_issuer
                  }

        self.__authn_request = request

    def get_request(self, deflate=True):
        """
        Returns unsigned AuthnRequest.
        :param deflate: It makes the deflate process optional
        :type: bool
        :return: AuthnRequest maybe deflated and base64 encoded
        :rtype: str object
        """
        if deflate:
            request = OneLogin_Saml2_Utils.deflate_and_base64_encode(self.__authn_request)
        else:
            request = b64encode(self.__authn_request)
        return request

    def get_id(self):
        """
        Returns the AuthNRequest ID.
        :return: AuthNRequest ID
        :rtype: string
        """
        return self.__id

    def get_xml(self):
        """
        Returns the XML that will be sent as part of the request
        :return: XML request body
        :rtype: string
        """
        return self.__authn_request
