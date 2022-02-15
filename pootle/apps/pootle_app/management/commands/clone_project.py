from email.mime import base
from django.forms import model_to_dict
from pootle_statistics.models import Submission, ScoreLog;
from pootle_app.models import Directory
from pootle_project.models import Project
from pootle_translationproject.models import TranslationProject
from django.core.management.base import BaseCommand, CommandError
from pootle_store.models import Store, Unit, Suggestion, QualityCheck;
import json;

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('project_id',type=int);


    def handle(self, *args, **options):
        project_id = options['project_id'];

        #maps an original id to its cloned model
        projectid_to_clone = {};
        directoryid_to_clone = {};
        translationid_to_clone = {};
        storeid_to_clone = {};
        unitid_to_clone = {};
        submissionsid_to_clone = {};
        suggestionid_to_clone = {};
        qualityid_to_clone = {};
        scorelogid_to_clone = {};
        
        project_clone = Project.objects.get(id=project_id);
        project_clone.id = None;
        project_clone.code = project_clone.code + "_clone";
        project_clone.fullname += "(CLONE)";
        

        directory = Directory.objects.get(id=project_clone.directory_id);
        directory.id = None;
        directory.name += "_clone";
        directory.save();
        directoryid_to_clone[project_clone.directory_id] = directory;

        project_clone.directory = directory;
        project_clone.save();
        projectid_to_clone[project_id] = project_clone;


        translations = TranslationProject.objects.filter(project_id=project_id);
        for translation in translations:
            translation_clone = TranslationProject.objects.get(id=translation.id);
            translation_id = translation.id;
            translation_clone.id = None;
            translation_clone.project = project_clone;
            translation_clone.save();
            translationid_to_clone[translation_id] = translation_clone;
            base_dir = translation.directory;

            stores = Store.objects.filter(translation_project_id=translation_id);
            for store in stores:
                store_clone = Store.objects.get(id=store.id);
                store_clone.id = None;
                print("init directory", store_clone.parent);
                print("base directory", base_dir);
                dirs = [store_clone.parent];

                while True:
                    
                    if(str(store.parent) == str(base_dir)):
                        store.parent.pootle_path = str(store.parent.pootle_path).replace(base_dir.name,base_dir.name + "_clone");
                        
                        break;
                    else:
                        store.parent.pootle_path = str(store.parent.pootle_path).replace(base_dir.name,base_dir.name + "_clone");
                        store.parent = store.parent.parent;
                        dirs.append(store.parent);
                base = None;

                isBaseDir = 1;
                if(str(store_clone.parent) != str(base_dir)):
                    #iterate thorugh all directories till base directory 
                    while store_clone.parent:
                        if(isBaseDir == 1):   #save the first parent
                            base = store_clone.parent;
                            isBaseDir = 0;
                        dir = store_clone.parent;
                        print('dir', dir)
                        dir.pootle_path = str(dir.pootle_path).replace(base_dir.name, base_dir.name + "_clone");
                        print("store_parent:",store_clone.parent);
                        store_clone.parent = store_clone.parent.parent; 

                        if(str(store_clone.parent) == str(base_dir)):
                            store_clone.parent.pootle_path = str(store_clone.parent.pootle_path).replace(base_dir.name, base_dir.name + "_clone");
                            break;
                else:
                    store_clone.parent.pootle_path = str(store_clone.parent.pootle_path).replace(base_dir.name, base_dir.name + "_clone");
                    base = store_clone.parent;
                
                store_clone.translation_project = translation_clone;
                store_clone.parent = base;
                print(store_clone.parent);
                print("new parent ",store_clone.parent);
                print("parent of parent", store_clone.parent.parent);
                print("parent of parent of parent", store_clone.parent.parent.parent);
                store_clone.name =  "clone_" + store_clone.name;

                store_clone.save();
                storeid_to_clone[store.id] = store_clone;

                #UNITS
                units = Unit.objects.filter(store_id=store.id);
                for unit in units:
                    unit_clone = Unit.objects.get(id=unit.id);
                    unit_clone.id = None;
                    unit_clone.store = store_clone;
                    unit_clone.save();
                    unitid_to_clone[unit.id] = unit_clone;
                    unitid_to_clone[unit.id] = unit_clone;
                    
            #submissions
            submissions = Submission.objects.filter(translation_project_id=translation.id);
            for submission in submissions:
                submission_clone = Submission.objects.get(id=submission.id);
                submission_clone.id = None;
                print("sub store");
                print(submission_clone.store);
                sub_store_id = submission_clone.store_id;
                if(sub_store_id  is not None):
                    if(sub_store_id in storeid_to_clone.keys()):
                        submission_clone.store = storeid_to_clone[sub_store_id];
                        print("existent clone store: ", submission_clone.store);
                
                submission_clone.translation_project = translation_clone;
                
                suggestion_id = submission_clone.suggestion_id;
                if suggestion_id is not None:
                    if suggestion_id in suggestionid_to_clone.keys():
                        suggestion_clone = suggestionid_to_clone[suggestion_id];
                        submission_clone.suggestion = suggestion_clone;

                    else:
                        suggestion_clone = Suggestion.objects.get(id=suggestion_id);
                        suggestion_clone.id = None;
                        sugg_unit_id = suggestion_clone.unit_id;

                        if(sugg_unit_id in unitid_to_clone.keys()):
                            suggestion_clone.unit = unitid_to_clone[sugg_unit_id];

                        suggestion_clone.save();
                        submission_clone.suggestion = suggestion_clone;
                    suggestionid_to_clone[suggestion_id] = suggestion_clone;

                quality_id = submission_clone.quality_check_id;
                if quality_id is not None:
                    if quality_id in qualityid_to_clone.keys():
                        submission_clone.quality_check_id = qualityid_to_clone[quality_id];
                    else:
                        quality_clone = QualityCheck.objects.get(id=quality_id);
                        quality_clone.id = None;
                        quality_clone.save();
                        qualityid_to_clone[quality_id] = quality_clone;

                submission_clone.save();
                submissionsid_to_clone[submission.id] = submission_clone;
                

        data = {'projects': projectid_to_clone,
                'directories': directoryid_to_clone,
                'translations': translationid_to_clone,
                'stores': storeid_to_clone,
                'units': unitid_to_clone,
                'submissions': submissionsid_to_clone,
                'suggestions': suggestionid_to_clone,
                'qualities': qualityid_to_clone,
                'scorelogs': scorelogid_to_clone};

        data = self.originalid_to_cloneid(data);
        return json.dumps(data);

    def originalid_to_cloneid(self,data):
        for model in data.keys():
            for originalid in data[model].keys():
                data[model][originalid] = data[model][originalid].id;
        
        return data;

