# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Buildings_damages
                                 A QGIS plugin
 This plugin estimates the percentage and the economic damage from flooding for each residential, commercial, industrial and transport building in a given area of interest, through the use of guidelines and Joint Research Centre's vulnerability curves and a space filling flood map.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-12-09
        copyright            : (C) 2022 by Giulia Mazzaccaro - Universit√† degli studi di Genova
        email                : giulia.mazzaccaro@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Giulia Mazzaccaro - Universit√† degli studi di Genova'
__date__ = '2022-12-09'
__copyright__ = '(C) 2022 by Giulia Mazzaccaro - Universit√† degli studi di Genova'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

"""
Model exported as python.
Name : Buildings_damages
Group : Buildings_damages
With QGIS : 32207
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Buildings_damages(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('rasterfloodingmap', 'Raster - flood map', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('vectorfilebuildings', 'Vector layer - Buildings', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Taxonomy', 'Taxonomy', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('VectorLayerAreaField', 'Vector layer - area field', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('VectorLayerGeometriesFixed', 'Vector layer - geometries fixed', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('BuildingLayerPercentageDamage', 'Building layer - Percentage damage', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('BuildingsLayerEconomicLosses', 'Buildings layer - Economic losses', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('VectorLayerDepthField', 'Vector layer - depth field', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Fix geometries
        alg_params = {
            'INPUT': parameters['vectorfilebuildings'],
            'OUTPUT': parameters['VectorLayerGeometriesFixed']
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['VectorLayerGeometriesFixed'] = outputs['FixGeometries']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Area',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Reale
            'FORMULA': ' $area',
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': parameters['VectorLayerAreaField']
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['VectorLayerAreaField'] = outputs['FieldCalculator']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Centroids
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 4,
            'FIELD_NAME': 'Building_typology',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Intero
            'FORMULA': 'CASE \r\nWHEN "def_cat_us" = \'Residenziale-Abitativa\' THEN 1\r\nWHEN "def_cat_us" = \'Residenziale\' THEN 1\r\n\r\nWHEN "def_cat_us" = \'Amministrativo\' THEN 2\r\nWHEN "def_cat_us" = \'Amministrativo-municipio\' THEN 2\r\nWHEN "def_cat_us" = \'Amministrativo-sede provincia\' THEN 2\r\nWHEN "def_cat_us" = \'Amministrativo-sede regione\' THEN 2\r\nWHEN "def_cat_us" = \'Amministrativo-sede ambasciata\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico- ASL - sede generica\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-ASL - sede di servizio socio assistenziale\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-ASL - sede di ospedale\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di clinica\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di poste-telegrafi\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di scuola, universit√†, laboratorio di ricerca\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di tribunale\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di polizia\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-sede di vigili del fuoco\' THEN 2\r\nWHEN "def_cat_us" = \'Servizio pubblico-casello forestale\' THEN 2\r\nWHEN "def_cat_us" = \'Militare\' THEN 2\r\nWHEN "def_cat_us" = \'Militare-Caserma\' THEN 2\r\nWHEN "def_cat_us" = \'Militare-Prigione\' THEN 2\r\nWHEN "def_cat_us" = \'Luogo di culto\' THEN 2\r\n\r\nWHEN "def_cat_us" = \'Servizi di trasporto\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto aereo\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto aereo - Aerostazione\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto aereo - Stazione eliporto\'THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale - Stazione autolinee\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale-parcheggio multipiano o coperto\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale-casello autostradale\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale-stazione di rifornimento carburante autostradale\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto stradale-stazione di rifornimento carburante stradale\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario- stazione passeggeri ferrovia\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario-deposito ferroviario per vagoni, rimessa locomotive\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario-casello ferroviario\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario-fermata ferroviaria\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto ferroviario-scalo merci\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione marittima\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione metropolitana\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione funivia\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione cabinovia\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione seggiovia\'THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione ski-lift\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-stazione funicolare\' THEN 4\r\nWHEN "def_cat_us" = \'Servizi di trasporto-altri impianti-edificio marittimo\'THEN 4\r\n \r\nWHEN "def_cat_us" = \'Commerciale\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-sede di banca\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-sede di centro commerciale\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-mercato\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-sede di supermercato, ipermercato\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-sede di albergo, locanda\' THEN 3\r\nWHEN "def_cat_us" = \'Commerciale-ostello della giovent√Ļ\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-stabilimento industriale\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-centrale elettrica\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-centrale termoelettrica\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-centrale idroelettrica\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-centrale nucleare\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-stazione/sottostazione elettrica\' THEN 3\r\nWHEN  "def_cat_us" = \'Industriale-impianto di produzione energia-stazione di trasformazione\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto di produzione energia-centrale eolica\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-impianto tecnologico\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-depuratore\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-inceneritore\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-stazione di telecomunicazioni\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-edificio di teleriscaldamento\' THEN 3\r\nWHEN "def_cat_us" = \'Industriale-edificio di area ecologica\' THEN 3\r\nWHEN "def_cat_us" = \'Agricolturale\' THEN 3\r\nWHEN "def_cat_us" = \'Agricolturale-fattoria\' THEN 3\r\nWHEN "def_cat_us" = \'Agricolturale-stalla\' THEN 3\r\nWHEN "def_cat_us" = \'Agricolturale-fienile\' THEN 3\r\n\r\n\r\nWHEN "def_cat_us" = \'Ricreativo\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali-biblioteca\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali-cinema\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali-teatro, auditorium\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali-museo\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† culturali-pinacoteca\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† sportive\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† sportive-piscina coperta\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† sportive-palestra\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-sede di attivit√† sportive-palaghiaccio\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-altre attivit√†\' THEN 2\r\nWHEN "def_cat_us" = \'Ricreativo-altre attivit√†-campeggio\' THEN 2\r\n\r\nELSE 0\r\n\r\nEND ',
            'INPUT': outputs['Centroids']['OUTPUT'],
            'OUTPUT': parameters['Taxonomy']
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Taxonomy'] = outputs['FieldCalculator']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'Max_ec_dam',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Reale
            'FORMULA': 'if( "Building_typology" = 1, ("Area"*739) ,if( "Building_typology" = 2, ("Area"*1028) ,if( "Building_typology" = 3, ("Area"*838) ,if( "Building_typology" = 4, ("Area"*21),0))))',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Raster sampling
        alg_params = {
            'COLUMN_PREFIX': 'Depth',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'RASTERCOPY': parameters['rasterfloodingmap'],
            'OUTPUT': parameters['VectorLayerDepthField']
        }
        outputs['RasterSampling'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['VectorLayerDepthField'] = outputs['RasterSampling']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Join attributes table
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Max_ec_dam'],
            'FIELD_2': 'id',
            'INPUT': parameters['vectorfilebuildings'],
            'INPUT_2': outputs['FieldCalculator']['OUTPUT'],
            'METHOD': 1,  # Prendi solamente gli attributi del primo elemento corrispondente (uno a uno)
            'PREFIX': '',
            'OUTPUT': parameters['BuildingsLayerEconomicLosses']
        }
        outputs['JoinAttributesTable'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BuildingsLayerEconomicLosses'] = outputs['JoinAttributesTable']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Field Calculator
        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'Perc_damage',
            'FIELD_PRECISION': 10,
            'FIELD_TYPE': 0,  # Reale
            'FORMULA': 'if( "Building_typology" = 1, ((0.0006* ("Depth1")^5)+(-0.0103* ("Depth1")^4)+( 0.0722*("Depth1")^3) +(-0.2528* ("Depth1")^2)+(0.5873* ("Depth1"))+ 0.0031) ,if( "Building_typology" = 2, ((-0.0004* ("Depth1")^5)+(0.0054* ("Depth1")^4)+(-0.0247*("Depth1")^3) +(0.0184* ("Depth1")^2)+(0.3051* ("Depth1"))- 0.0013) ,if( "Building_typology" = 3, ((-0.0007* ("Depth1")^5)+(0.0097* ("Depth1")^4)+(-0.0431*("Depth1")^3) +(0.0537* ("Depth1")^2)+(0.255* ("Depth1"))+ 0.0033) ,if( "Building_typology" = 4, ((-0.0007* ("Depth1")^6)+(0.0125* ("Depth1")^5)+(-0.0833*("Depth1")^4) +(0.265* ("Depth1")^3)+(-0.4939* ("Depth1")^2)+(0.8364* ("Depth1"))-0.0012),0))))',
            'INPUT': outputs['RasterSampling']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Joint attributes table
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'id',
            'FIELDS_TO_COPY': ['Perc_damage'],
            'FIELD_2': 'id',
            'INPUT': parameters['vectorfilebuildings'],
            'INPUT_2': outputs['FieldCalculator']['OUTPUT'],
            'METHOD': 1,  # Prendi solamente gli attributi del primo elemento corrispondente (uno a uno)
            'PREFIX': '',
            'OUTPUT': parameters['BuildingLayerPercentageDamage']
        }
        outputs['JointAttributesTable'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BuildingLayerPercentageDamage'] = outputs['JointAttributesTable']['OUTPUT']
        return results

    def name(self):
        return 'Buildings_damages'

    def displayName(self):
        return 'Buildings_damages'

    def group(self):
        return 'Buildings_damages'

    def groupId(self):
        return 'Buildings_damages'

    def createInstance(self):
        return Buildings_damages()
