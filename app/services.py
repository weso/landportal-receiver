from app import db
from model import models


class ParserService(object):

    def parse_nodes_content(self, content):
        """Parse a XML file and return the corresponding model.

        Parse a XML (the XML file must conform with the Landportal schema)
        to create an object representation based on the Landportal-model.
        Returns the root of the model-tree (the Dataset).
        """
        import xml.etree.ElementTree as Et
        root_node = Et.fromstring(content)
        dataset = self._parse_dataset(root_node)
        return dataset

    def _parse_dataset(self, node):
        """Parse a dataset node and return a Dataset object."""
        dataset = models.Dataset()
        datasource = self._parse_datasource(node.find('import_process').find('datasource'))
        dataset.datasource = datasource
        license = self._parse_license(node.find('license'))
        dataset.license = license
        # Dataset indicators
        # indicators = {}
        # for item in node.find('indicators').findall('indicator'):
        #     ind = self._parse_indicator(item, dataset)
        #     indicators[ind.id_source] = ind
        # Dataset compound indicators
        #comp_indicators = []
        #for item in node.find('indicators').findall('compound_indicator'):
        #    comp_indicators.append(self._parse_compound_indicator(item, dataset, indicators))
        #return dataset
        # Dataset observations
        #for item in node.find('observations').findall('observation'):
        #    self._parse_observation(item, dataset, indicators)
        return dataset

    def _parse_datasource(self, node):
        """Parse a datasource node and return a Datasource object."""
        datasource = models.DataSource(id_source=node.text)
        return datasource

    def _parse_license(self, node):
        """Parse a license node and return a License object."""
        license = models.License(name=node.find('lic_name').text,
                                 description=node.find('lic_description').text,
                                 republish=bool(node.find('republish').text),
                                 url=node.find('lic_url').text)
        return license

    def _parse_indicator(self, node, dataset):
        """Parse an indicator node and return an Indicator object."""
        id_source = node.get('id')
        name = node.find('ind_name').text
        description = node.find('ind_description').text
        measurement = self._parse_measurement(node.find('measure_unit'))

        indicator = models.Indicator(id_source=id_source,
                                     name=name,
                                     description=description,
                                     )
        indicator.measurement_unit = measurement
        indicator.dataset = dataset
        return indicator

    def _parse_measurement(self, node):
        """Parse a measurement node and return a MeasurementUnit object."""
        measurement = models.MeasurementUnit(name=node.text)
        return measurement

    def _parse_compound_indicator(self, node, dataset, indicators):
        """Parse a compound indicator node and return a CompoundIndicator object."""
        id_source = node.get('id')
        name = node.find('ind_name').text
        description = node.find('ind_description').text
        measurement = self._parse_measurement(node.find('measure_unit'))

        indicator = models.CompoundIndicator(id_source=id_source,
                                             name=name,
                                             description=description,
                                             )
        indicator.measurement_unit = measurement
        indicator.dataset = dataset
        for rel in node.findall('indicator-ref'):
            # Buscar el indicador que sea en la coleccion de indicadores y
            # establecer en dicho indicador que esta relacionado con este
            print rel.get('id')
            indicators[rel.get('id')].compound_indicator = indicator
        return indicator

    def _parse_observation(self, node, dataset, indicators):
        id_source = node.get('id')
        # TODO: parse issued
        obs_status = node.find('obs_status').text
        # TODO: parse value
        # TODO: parse computation
        # TODO: parse country
        # TODO: parse time (ref-time)
        # TODO: parse indicator group
        # TODO: parse region
        # TODO: parse slice
        rel_indicator_id = node.find('indicator-ref').get('id')

        # Meter los atributos que sean
        observation = models.Observation()
        observation.indicator = indicators[rel_indicator_id]
        observation.dataset = dataset

        return observation

