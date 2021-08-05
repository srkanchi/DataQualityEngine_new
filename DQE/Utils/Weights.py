########### A trials
weights = {

        "dictionary_TD": {
                "crops.name":"Crop name",
                "keywords": "keyword - Objectives",
                "externalField": "External field",
                "fieldTestingType": "Testing type",
                "projectNumbers": "Project number",
                "siteType": "Site type",
                "plotArea": "Plot area", 
                "plannedTotalNumberOfTrials":"Planned number of trials",
                "experimentalSeason": "Experimental season", 
                "targets.name":"Target name"
        },


        "weights_TD_0": {
                "tptIdKey": 0,
                "crops":0,
                "crops.name":5,
                "keywords": 5,
                "projectNumbers": 5,
                "trialResponsibles": 0,
                "trialResponsibles.hasName": 4,
                "trialResponsibles.testType": 5,
                "trialResponsibles.internalValue": 5,
                "trialResponsibles.siteName": 5,
                "trialResponsibles.plannedNumberOfTrials": 5,
                "siteType": 5,
                "plannedNumberOfApplications":5,
                "numberOfReplicates": 5, 
                "experimentalSeason": 4, 
                "targets": 0,
                "targets.name":5
        },

        "weights_TD_0_CROPSAFETY": {
                "tptIdKey": 0,
                "crops":0,
                "crops.name":5,
                "keywords": 5,
                "projectNumbers": 5,
                "trialResponsibles": 0,
                "trialResponsibles.hasName": 4,
                "trialResponsibles.testType": 5,
                "trialResponsibles.internalValue": 5,
                "trialResponsibles.siteName": 5,
                "trialResponsibles.plannedNumberOfTrials": 5,
                "siteType": 5,
                "plannedNumberOfApplications":4,
                "numberOfReplicates": 5, 
                "experimentalSeason": 4, 
                "targets": 0,
                "targets.name":0
        },


#                "treatments.assessmentMeanValues.numberOfSubsamples": 1,


        "weights_TD_1": {
                "tptIdKey": 0,
                "dataDeadline": 5,
                "gepCode":  5,
                "guidelines":  5,
                "keywords":  5,
                "plannedNumberOfApplications":  5,
                "plannedNumberOfAssessments":  5,
                "treatments": 0,
                "treatments.applications": 0,
                "treatments.applications.crops": 0, 
                "treatments.applications.crops.cropStageCode": 5,
                "treatments.applications.applicationCode": 5,
                "treatments.applications.products": 0,
                "treatments.applications.products.equipment": 0,
                "treatments.applications.products.equipment.method": 5,
                "treatments.applications.products.equipment.placement": 5             
        },

        "weights_TD_1_ASSESS": {
                "plannedAssessments": 0, 
                "plannedAssessments.standardEvaluationId": 5,
                "plannedAssessments.sampleSize": 5,
                "plannedAssessments.sampleSizeUnit": 5,
                "plannedAssessments.assessmentCode": 5,
                "plannedAssessments.partRated": 5,
                "plannedAssessments.ratingType": 5,
                "plannedAssessments.calculated": 0, 
                "plannedAssessments.crop": 5, 
                "plannedAssessments.crop.name": 5, 
                "plannedAssessments.target": 5,
                "plannedAssessments.target.name": 5

        },

        "weights_TD_1_ASSESS_PH": {
                "plannedAssessments": 0, 
                "plannedAssessments.standardEvaluationId": 5,
                "plannedAssessments.sampleSize": 5,
                "plannedAssessments.sampleSizeUnit": 5,
                "plannedAssessments.assessmentCode": 5,
                "plannedAssessments.partRated": 0,
                "plannedAssessments.ratingType": 5,
                "plannedAssessments.calculated": 0, 
                "plannedAssessments.crop": 0, 
                "plannedAssessments.crop.name": 0, 
                "plannedAssessments.target": 0,
                "plannedAssessments.target.name": 0
        },


        "weights_A_I": {
                "name": 0,
                "tillageType": 0,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":0,
                "crops.plantingRate":0,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },

        "weights_A_F" : {
                "name": 0,
                "tillageType": 0,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":0,
                "crops.plantingRate":0,
                "irrigations":0,
                "irrigations.date": 5,
                "irrigations.amount": 5,
                "irrigations.amountUnit": 5,
                "irrigations.equipmentType": 5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.ratingType": 5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.numberOfSubsamples": 5,
                "treatments.assessmentMeanValues.target": 5,
                "treatments.assessmentMeanValues.crop": 5,
                "treatments.assessmentMeanValues.crop.name": 5,
                "treatments.assessmentMeanValues.target.name": 5,
                "treatments.assessmentMeanValues.meanQuantity": 5,
                "treatments.assessmentMeanValues.cropStage": 5
        },

        "weights_A_H" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },


        "weights_A_S" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },


        ################### R Trials

        "weights_R_I" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },

        "weights_R_F" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },

        "weights_R_H" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },


        "weights_R_S" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },



        ################# D Trials

        "weights_D_I" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },

        "weights_D_F" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },

        "weights_D_H" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.ratingClass": 5
        },


        "weights_D_S" : {
                "name": 0,
                "tillageType": 5,
                "location":0,
                "location.country": 5,
                "location.latitude": 5,
                "location.longitude": 5,
                "crops":0,
                "crops.name":5,
                "crops.variety":5,
                "crops.plantingDate":5,
                "crops.plantingRate":5,
                "treatments":0,
                "treatments.assessmentMeanValues.partRated":5,
                "treatments.assessmentMeanValues.ratingType": 5,
                "treatments.assessmentMeanValues.date": 5,
                "treatments.assessmentMeanValues.sampleSize": 5,
                "treatments.assessmentMeanValues.sampleSizeUnit": 5,
                "treatments.assessmentMeanValues.numberOfSubsamples": 5,
                "treatments.assessmentMeanValues.target": 5,
                "treatments.assessmentMeanValues.crop": 5,
                "treatments.assessmentMeanValues.crop.name": 5,
                "treatments.assessmentMeanValues.target.name": 5,
                "treatments.assessmentMeanValues.meanQuantity": 5,
                "treatments.assessmentMeanValues.cropStage": 5

        }




}


dictionary_TD = {
        "name": "TD_name",
        "crops.name":"Crop_name",
        "keyword": "Keyword-Objective",
        "testType": "Test_type",
        "projectNumbers": "Project_number",
        "responsibleSite": "Responsible_site_code",
        "GEPLevel": "GEP_level",
        "guidelines": "Guidelines",
        "siteType": "Site_type",
        "plotArea": "Plot_area",
        "experimentalSeason": "Experimental_season", 
        "targets.name":"Target_name",
        "technicalManager": "Techn_manager",
        "locationControl": "Location_of_control",
        "dataDeadline": "Data_deadline",
        "treatments.applications.products.equipment.method": "Application_method",
        "treatments.assessmentMeanValues.partRated":"Part_rated",
        "treatments.assessmentMeanValues.ratingType": "Rating_type",
        "treatments.assessmentMeanValues.sampleSize": "Sample_size",
        "treatments.assessmentMeanValues.sampleSizeUnit": "Sample_size_unit",
        "treatments.assessmentMeanValues.numberOfSubsamples": "Number_Subsamples",
        "treatments.assessmentMeanValues.crop.name": "Crop_name",
        "treatments.assessmentMeanValues.target.name": "Target_name",
        "treatments.assessmentMeanValues.standardEvaluation": "Standard_evaluation",
        "treatments.assessmentMeanValues.assessmentCode": "Assessment_code"
}

styles_TD = {
        "TD_name": "present",
        "Crop_name": "present",
        "Keyword-Objective": "present",
        "Test_type": "present",
        "Project_number": "present",
        "Responsible_site_code": "present",
        "GEP_level": "present",
        "Guidelines": "present",
        "Site_type": "present",
        "Plot_area": "present",
        "Experimental_season": "present", 
        "Target_name": "present",
        "Techn_manager": "present",
        "Location_of_control": "present",
        "Data_deadline": "present",
        "Application_method": "present",
        "Part_rated": "present",
        "Rating_type": "present",
        "Sample_size": "present",
        "Sample_size_unit": "present",
        "NumberSubsamples": "present",
        "Crop_name": "present",
        "Target_name": "present",
        "Standard_evaluation": "present",
        "Assessment_code": "present"
}


