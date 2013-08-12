#!/usr/bin/python
from xml.etree.ElementTree import Element
from nassl._nassl import OCSP_RESPONSE


class OcspResponse:
    """
    High level API for parsing an OCSP response.
    """


    def __init__(self, ocspResp):
        self._ocspResp = ocspResp 
        
    
    def as_text(self):
        return self._ocspResp.as_text()
        
        
    def verify(self, verifyLocations):
        return self._ocspResp.basic_verify(verifyLocations)


    def as_dict(self):
        # For now we just parse OpenSSL's text output and make a lot of assumptions
        respDict = { \
            'responseStatus': self._get_value_from_text_output_no_p('OCSP Response Status:'),
            'version' : self._get_value_from_text_output_no_p('Version:'),
            'responseType': self._get_value_from_text_output('Response Type:'),
            'responderID': self._get_value_from_text_output('Responder Id:'),
            'producedAt': self._get_value_from_text_output('Produced At:')}

        if 'successful' not in respDict['responseStatus']:
            return respDict

        respDict['responses'] = [ { \
            'certID': { 
                'hashAlgorithm': self._get_value_from_text_output('Hash Algorithm:'),
                'issuerNameHash': self._get_value_from_text_output('Issuer Name Hash:'),
                'issuerKeyHash': self._get_value_from_text_output('Issuer Key Hash:'),
                'serialNumber': self._get_value_from_text_output('Serial Number:')
                },
            'certStatus': self._get_value_from_text_output('Cert Status:'),
            'thisUpdate': self._get_value_from_text_output('This Update:'),
            'nextUpdate': self._get_value_from_text_output('Next Update:')
            }]
        
        return respDict


    def as_xml(self):
        ocspXml = []
        for (key, value) in self.as_dict().items():
            for xmlElem in self._keyvalue_pair_to_xml(key, value):
                ocspXml.append(xmlElem)
        
        return ocspXml


# XML functions
    def _keyvalue_pair_to_xml(self, key, value=''):
        res_xml = []
        
        if type(value) is str: # value is a string
            key_xml = self._create_xml_node(key)
            key_xml.text = value
            res_xml.append(key_xml)
            
        elif value is None: # no value
            res_xml.append(self._create_xml_node(key))
           
        elif type(value) is list: # the list of responses; only 1 for now
            key_xml = self._create_xml_node(key)
            print key
            print value
            key_xml.append(self._keyvalue_pair_to_xml('response', value[0]))
            res_xml.append(key_xml)

        elif type(value) is dict: # value is a list of subnodes
            key_xml = self._create_xml_node(key)
            for subkey in value.keys():
                for subxml in self._keyvalue_pair_to_xml(subkey, value[subkey]):
                    key_xml.append(subxml)
                 
            res_xml.append(key_xml)
            
        return res_xml    


    def _create_xml_node(self, key, value=''):
        key = key.replace(' ', '').strip() # Remove spaces
                
        xml_node = Element(key)
        xml_node.text = value.decode( "utf-8" ).strip()
        return xml_node
    

# Text parsing
    def _get_value_from_text_output(self, key):
        value = self._ocspResp.as_text().split(key)
        return value[1].split('\n')[0].strip()


    def _get_value_from_text_output_no_p(self, key):
        value = self._ocspResp.as_text().split(key)
        value = value[1].split('\n')[0].strip()
        return value.split('(')[0].strip()


