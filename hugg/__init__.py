import os, sys,types,importlib.machinery
from pathlib import Path
from huggingface_hub import HfApi

class face(object):
    def __init__(self,repo,use_auth=True,repo_type="dataset",clear_cache=False):
        """
        https://rebrand.ly/hugface

        https://huggingface.co/docs/huggingface_hub/quick-start
        https://huggingface.co/docs/huggingface_hub/how-to-upstream
        https://huggingface.co/docs/huggingface_hub/how-to-downstream
        """

        self.api = HfApi()
        self.repo = repo
        self.repo_type = repo_type
        self.auth = use_auth
        self.downloaded_files = []
        self.opened = False
        self.clear_cache = clear_cache

    def clearcache(self):
        if self.clear_cache:
            pathings = [x for x in os.walk(Path.home()) if self.repo.replace('/','--') in x]
            if len(pathings) > 0:
                try:
                    for y in pathings:
                        os.system("yes|rm -r " + str(y))
                except:
                    pass

    def open(self):
        if isinstance(self.auth,str):
            hugging_face = f"{str(Path.home())}/.huggingface/"
            import os
            if not os.path.exists(os.path.join(hugging_face,"token")):
                for cmd in [
                    f"mkdir -p {hugging_face}",
                    f"rm {hugging_face}/token",
                    f"touch {hugging_face}/token"
                ]:
                    try:
                        print(cmd);os.system(cmd)
                    except:
                        pass

                with open(f"{hugging_face}/token","a") as writer:
                    writer.write(self.auth)
            self.auth = True
        self.clearcache()
        self.opened = True
        return
    def close(self):
        for foil in self.downloaded_files:
            try:
                os.remove(foil)
            except:
                try:
                    os.system("yes|rm " + str(foil))
                except Exception as e:
                    print("Failed to remove the cached file " +str(foil))
                    print(e)
                    pass
        self.clearcache()
        return
    def download(self, file_path=None,revision=None,download_to=None):
        if not self.opened:
            self.open()
        #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/file_download#huggingface_hub.hf_hub_download
        if file_path and isinstance(file_path,str):
            from huggingface_hub import hf_hub_download
            current_file = hf_hub_download(
                repo_id=self.repo,
                filename=file_path,
                revision=revision,
                repo_type=self.repo_type,
                use_auth_token=self.auth
            )
            if download_to:
                try:
                    os.rename(current_file,download_to)
                    current_file = download_to
                except:
                    pass
            return current_file
        return None
    def upload(self, path=None,path_in_repo=None):
        if not self.opened:
            self.open()
        if path:
            if isinstance(path,str) and os.path.isfile(path):
                #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.upload_file
                self.api.upload_file(
                    path_or_fileobj=path,
                    path_in_repo=path_in_repo or path,
                    repo_id=self.repo,
                    repo_type=self.repo_type,
                )
            elif isinstance(path,str) and os.path.isdir(path):
                #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.upload_folder
                self.api.upload_file(
                    folder_path=path,
                    path_in_repo=path_in_repo or path,
                    repo_id=self.repo,
                    repo_type=self.repo_type,
                )
            else:
                print("Entered path " + stsr(path) + " is not supported.")
            return True
        return False
    def files(self,revision=None):
        if not self.opened:
            self.open()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.list_repo_files
        return self.api.list_repo_files(
            repo_id=self.repo,
            revision=revision,
            repo_type=self.repo_type
        )
    def impor(self,file):
        if file not in self.files():
            print("FILE IS NOT AVAILABLE")
            return None
        
        import_name = str(file.split('/')[-1]).replace('.py','')
        #https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3#answer-19011259
        loader = importlib.machinery.SourceFileLoader(import_name, os.path.abspath(self[file]))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)

        return mod
        
    def delete_file(self,path_in_repo=None,revision=None):
        if not self.opened:
            self.open()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.delete_file
        if path_in_repo:
            self.api.delete_file(
                path_in_repo=path_in_repo,
                repo_id=self.repo,
                repo_type=self.repo_type,
                revision=revision
            )
        return False

    def find_all(self,lambda_search,grab=True):
        return [self[x] if grab else x for x in self.files() if lambda_search(x)]

    def find(self,lambda_search,grab=True):
        current = self.find_all(lambda_search,False)
        if len(current) > 1:
            print("There are too many files found")
        elif len(current) == 1:
            return self[current[0]] if grab else current[0]
        return None

    def __enter__(self):
        self.open()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return self
    def __iadd__(self, path):
        self.upload(path)
        return self
    def __getitem__(self,foil):
        return self.download(foil)
    def __setitem__(self,key,value):
        self.upload(value,key)
    def __delitem__(self,item):
        return self.delete_file(item)
    def __str__(self):
        return self.files()
    def __contains__(self, item):
        return item in self.files()
    def __call__(self,item):
        return self.download(item) if item in self else None
