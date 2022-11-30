import os,sys,types,importlib.machinery,shutil
from pathlib import Path
from huggingface_hub import HfApi
from github import Github
from abc import ABC, abstractmethod

class mem(object):    
    @abstractmethod
    def login(self):
        pass
    
    @abstractmethod
    def logut(self):
        pass

    @abstractmethod
    def files(self):
        pass
    
    @abstractmethod
    def upload(self, path=None,path_in_repo=None):
        pass

    @abstractmethod
    def download(self, file_path=None,download_to=None):
        pass

    @abstractmethod
    def delete_file(self,path_in_repo=None):
        pass
    
    def __enter__(self):
        self.login()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
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
    
    def find_all(self,lambda_search,grab=True):
        return [self[x] if grab else x for x in self.files() if lambda_search(x)]

    def find(self,lambda_search,grab=True):
        current = self.find_all(lambda_search,False)
        if len(current) > 1:
            print("There are too many files found")
        elif len(current) == 1:
            return self[current[0]] if grab else current[0]
        return None

"""
class face(mem):
    def __init__(self,repo,use_auth=True,repo_type="dataset",clear_cache=False):
        super().__init__(type="HuggingFace")
    def login(self):
    def logout(self):
    def download(self, file_path=None,download_to=None):
    def upload(self, path=None,path_in_repo=None):
    def files(self):
    def delete_file(self,path_in_repo=None):
"""

class face(mem):
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

    def login(self):
        if isinstance(self.auth,str):
            hugging_face = os.path.join(Path.home(),".huggingface")
            token_path = os.path.join(hugging_face, "token")
            import os
            if not os.path.exists(os.path.join(hugging_face,"token")):
                for cmd in [
                    f"mkdir -p {hugging_face}",
                    f"rm {token_path}",
                    f"touch {token_path}"
                ]:
                    try:
                        print(cmd);os.system(cmd)
                    except:
                        pass

                with open(token_path,"a") as writer:
                    writer.write(self.auth)
            self.auth = True
        self.clearcache()
        self.opened = True
        return
    def logout(self):
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
    def download(self, file_path=None,download_to=None):
        if not self.opened:
            self.login()
        #https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/file_download#huggingface_hub.hf_hub_download
        if file_path and isinstance(file_path,str):
            from huggingface_hub import hf_hub_download
            current_file = hf_hub_download(
                repo_id=self.repo,
                filename=file_path,
                repo_type=self.repo_type,
                use_auth_token=self.auth
            )
            if download_to:
                try:
                    shutil.copy(current_file, os.path.basename(current_file))
                    current_file = os.path.basename(current_file)
                except:
                    pass
            return current_file
        return None
    def upload(self, path=None,path_in_repo=None):
        if not self.opened:
            self.login()
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
    def files(self):
        if not self.opened:
            self.login()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.list_repo_files
        return self.api.list_repo_files(
            repo_id=self.repo,
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
        
    def delete_file(self,path_in_repo=None):
        if not self.opened:
            self.login()
        # https://huggingface.co/docs/huggingface_hub/v0.9.0/en/package_reference/hf_api#huggingface_hub.HfApi.delete_file
        if path_in_repo:
            self.api.delete_file(
                path_in_repo=path_in_repo,
                repo_id=self.repo,
                repo_type=self.repo_type
            )
        return False

class ghub(mem):
    def __init__(self,repo,access_token,branch=None):
        self.repo = Github(access_token).get_repo(repo)
        
        self.branch = None
        if branch is not None:
            self.branch = branch
        
        if self.branch is None:
            try:
                self.repo.get_branch(branch="main")
                self.branch = "main"
            except Exception as e:
                print(e)
                print("Branch 'main' does not exist")
                pass
        
        if self.branch is None:
            try:
                self.repo.get_branch(branch="master")
                self.branch = "master"
            except Exception as e:
                print(e)
                print("Branch 'master' does not exist")
                pass

        if self.branch is None:
            print("No branch is selected, cannot work")
            self.repo = None

    def files(self):
        files = []
        contents = self.repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                files += [file_content.path]
        return files

    def login(self):
        return
    def logout(self):
        return
    def download(self, file_path=None,download_to=None):
        if download_to is None:
            download_to = os.path.join(os.curdir,file_path.split("/")[-1])
        if file_path and isinstance(file_path,str):
            with open(download_to,"w+") as writer:
                writer.write(self.repo.get_contents(file_path).decoded_content.decode("utf-8") )
        return download_to
    def upload(self, file_path=None,path_in_repo=None):
        if path_in_repo in self: #Update
            from pathlib import Path
            contents = self.repo.get_contents(path_in_repo, ref=self.branch) #https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/Repository.py#L1803
            new_contents = Path(file_path).read_text()
            self.repo.update_file(contents.path, "Updating the file {}".format(path_in_repo), new_contents, contents.sha, branch=self.branch) #https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/Repository.py#L2134
        else: #Create #https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/Repository.py#L2074
            self.repo.create_file(path_in_repo, "Creating the file {}".format(path_in_repo), file_path, branch=self.branch)
    def delete_file(self,path_in_repo=None):
        if path_in_repo in self.files():
            contents = self.repo.get_contents(path_in_repo, ref=self.branch) #https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/Repository.py#L1803
            self.repo.delete_file(path_in_repo, "Deleting the file {}".format(path_in_repo), contents.sha,branch=self.branch) #https://github.com/PyGithub/PyGithub/blob/001970d4a828017f704f6744a5775b4207a6523c/github/Repository.py#L2198
