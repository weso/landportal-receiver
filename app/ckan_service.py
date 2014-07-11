__author__ = 'guillermo'
import ckanapi
import os
from parser import Parser
import config


class ReceiverCKANService(object):
    """
    Service that gets the file input from the html request and uploads it to CKAN
    instance
    """
    def __init__(self, content, api_key):
        self.parser = Parser(content.encode(encoding='utf-8'))
        self.api_key = api_key

    def run_service(self, file_, ckan_instance):
        ckan_site = ckanapi.RemoteCKAN(ckan_instance, apikey=self.api_key)
        org = self._create_organization(ckan_site)
        data_set = self._create_package(org=org, site=ckan_site)
        self._create_resource(data_set=data_set, file_=file_, site=ckan_site)

    def _get_org_logo(self):
        org_uri = self.parser.get_organization().id
        org_img = config.SOURCE_IMG_PATH
        for key in config.SOURCE_IMG.keys():
            if key in org_uri:
                org_img += config.SOURCE_IMG[key]
        return org_img

    def _create_organization(self, site):
        """ Creates a new organization
        Checks if the organization does not exists in database and if not creates it
        :param site:
        :return:org_uri
        """
        org_name = self.parser.get_organization().name
        org_uri = self.parser.get_organization().id.lower()
        org_desc = self.parser.get_organization().description
        org_logo = self._get_org_logo()
        organizations = site.action.organization_list(order_by="name")
        if org_uri not in organizations:
            site.action.organization_create(name=org_uri, title=org_name,
                                            description=org_desc,
                                            image_url=org_logo)
        return org_uri

    def _create_package(self, org, site):
        """ Creates a new data set
        Checks if the data set does not exists and if it's owned by an organization
        :param org:
        :param site:
        :return:data_set_uri
        """
        print "Creating dataset ..."
        data_set_id = self.parser.get_dataset().id
        data_set_uri = self.parser.get_dataset().id.lower()
        data_sets = site.action.package_list()
        if org and data_set_uri not in data_sets:
            site.action.package_create(name=data_set_uri, title=data_set_id,
                                       owner_org=org)
        return data_set_uri

    def _create_resource(self, data_set, site, file_):
        """ Creates a new resource or file associated with its data set
        :param data_set:
        :param site:
        :param file_:
        """
        file_name = file_.filename
        path = os.path.join(config.DATA_SETS_DIR, file_.filename)
        file_.save(path)
        url = self.parser.get_file_name()
        site.action.resource_create(package_id=data_set, upload=open(path),
                                    name=file_name, url=url)


