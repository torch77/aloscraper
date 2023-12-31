import urllib.request
import socket
import os
import time
import getpass
import _thread
import re
from tqdm import tqdm
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import ffmpeg


REDOWNLOAD = False
# BASEPATH = os.getcwd() + "\\content"
# BASEPATH = r"M:\Serien\Aloyoga"

socket.setdefaulttimeout(10)
# email = input('Enter Email:')
email = 'torch77@gmail.com'
# password = getpass.getpass(prompt='Enter Password:')
password = '6!&5kilSW!i9#PApktb@'
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')
browser = webdriver.Chrome(options=options)
# browser = webdriver.Chrome()
paths = []
lines = []
LINKFILE = ""
BASEPATH = ""
SYSTEM = os.name

#6!&5kilSW!i9#PApktb@
if SYSTEM == "nt":
    LINKFILE = os.getcwd() + "\\downloadlinks.txt"
    with open(LINKFILE) as f:
        lines = [line.rstrip() for line in f]
    for line in lines:
        line = line.split("series")[1].split("workouts")[0]
        paths.append(BASEPATH + "\\" + line[1:-1]
                     + "\\")
    for path in paths:
        path.replace("/", "\\")
elif SYSTEM == "posix":
    LINKFILE = os.getcwd() + "/downloadlinks.txt"
    with open(LINKFILE) as f:
        lines = [line.rstrip() for line in f]
    for line in lines:
        line = line.split("series")[1].split("workouts")[0]
        paths.append(BASEPATH + line)
else:
    print("OS not supported, please open an issue on Github.")

print(paths)


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def downloadmp4(url, filename, path, counterepisode, counterseason):
    fullname = path + f"s{str(counterseason+1).zfill(2)}" + f"e{str(counterepisode+1).zfill(2)}_" + filename + ".mp4"
    fullname = fullname.lower()
    if os.path.isfile(fullname):
        print(filename + " already exists, skipping...")
        return True
    else:
        print("Downloading: " + filename)
        # with DownloadProgressBar(unit='B', unit_scale=True,
                                #  miniters=1, desc=url.split('/')[-1]) as t:
        try:
            urllib.request.urlretrieve(
                url, filename=fullname, reporthook=t.update_to)
            return True
        except:
            print("Request timed out!")
            try:
                os.remove(fullname)
            except:
                print("No file created!")
                return False
            return False
        

def downloadm3u8_as_mkv(url, filename, path, counterepisode, counterseason):
    fullname = path + f"s{str(counterseason+1).zfill(2)}" + f"e{str(counterepisode+1).zfill(2)}_" + filename + ".mkv"
    fullname = fullname.lower()
    if os.path.isfile(fullname):
        print(filename + " already exists, skipping...")
        return True
    else:
        print("Downloading: " + filename)
        print(url)
        try:
            ffmpeg.input(url).output(fullname).global_args('-progress', 'pipe:1').run(capture_stdout=True, capture_stderr=True)
            return True
        except ffmpeg.Error as e:
            print('stdout:', e.stdout)
            print('stderr:', e.stderr)
            raise e
        except:
            print("Request timed out!")
            try:
                os.remove(fullname)
            except:
                print("No file created!")
                return False
            return False

def doLogin(email, password):
    browser.get(
        "https://www.alomoves.com/signin")
    time.sleep(5)
    mailfield = browser.find_element("xpath",
        "//input[contains(@name,'email')]")
    pwfield = browser.find_element("xpath",
        "//input[contains(@name,'password')]")
    mailfield.send_keys(email)
    mailfield.send_keys(Keys.TAB)
    time.sleep(1)
    pwfield.send_keys(password)
    pwfield.send_keys(Keys.ENTER)


def collectClasses(courselink):
    print(f"== Grabbing links for {courselink} ==")
    time.sleep(5)
    browser.get(courselink)
    time.sleep(5)
    workoutLinks = browser.find_elements("xpath",
        "//div[contains(@class,'workout-title')]/a")
    reallinks = [link.get_attribute("href") for link in workoutLinks]
    if(len(reallinks) == 0):
        print("Login failed, make sure you got a valid trial account!")
        browser.quit()
        quit(1)
    return reallinks


def grabLesson(lessonlink, path):
    browser.get(lessonlink)
    # time.sleep(2)
    try:
        # videolink = browser.find_element("tag name",
        # "video").get_attribute("currentSrc")
        # https://github.com/wkeeling/selenium-wire#accessing-requests
        videolink = browser.wait_for_request('m3u8').url
        # videotitle = browser.find_element("tag name",
        # "h1").get_attribute("innerText").replace(":", "").replace(" ", "_").replace("/", "")
        videotitle = browser.find_element(By.CLASS_NAME, "workoutTitle").text
    except:
        print("Page loading failed! Retrying...")
        return False
    return [videolink, videotitle]


def makeDir(dirr):
    try:
        os.makedirs(dirr)
    except OSError:
        pass

# paths = ['\\desk-therapy\\']

# # drop beginner strength for now, need to handle classes w/ repeated videos
# paths.remove('\\beginner-true-strength\\')
# paths.remove('\\true-strength-fundamentals\\')
# paths.remove('\\quest-for-the-press\\')
# lines = ['https://www.alomoves.com/series/desk-therapy/workouts']
REDOWNLOAD = False
## need to set basepath to out of C drive


def main():
    doLogin(email, password)
    for i in range(len(lines)):
        GOTONEXT = False
        counter = 0
        failures = 0
        skipped = 0
        if(os.path.exists(paths[i])):
            if not REDOWNLOAD:
                print(f"Course {paths[i]} already exists, skipping ...")
                GOTONEXT = True
            else:
                lessonlinks = collectClasses(lines[i])
                makeDir(paths[i])
        else:
                lessonlinks = collectClasses(lines[i])
                makeDir(paths[i])
        if not GOTONEXT:
            dlcontent = []
            while counter < len(lessonlinks):
                print(
                    f"Grabbed {counter}/{len(lessonlinks)-1} links ({skipped} skipped)")
                del browser.requests
                result = grabLesson(lessonlinks[counter], paths[i])
                if not result:
                    failures += 1
                    time.sleep(15)
                    if failures == 3:
                        print("Something wrong with the link, skipping...")
                        dlcontent.append(["Null","Null"])
                        counter += 1
                        skipped += 1
                        failures = 0
                else:
                    dlcontent.append(result)
                    counter += 1
            counter = 0
            failures = 0
            while counter < len(dlcontent):
                print(f"{counter}/{len(dlcontent)-1} files downloaded")
                # if not downloadmp4(dlcontent[counter][0], dlcontent[counter][1], paths[i], counter, i):
                if not downloadm3u8_as_mkv(dlcontent[counter][0], dlcontent[counter][1], paths[i], counter, i):
                    failures += 1
                    time.sleep(15)
                    if failures == 3:
                        print("Cant grab link, skipping...")
                        counter += 1
                        failures = 0
                else:
                    counter += 1
    browser.quit()
    print("++ All downloads completed, have fun! ++")
    quit(0)


main()


### to do 
### don't download all videos for each class if it is repeated 
### double check how we're getting m3u8 links, looked to be dpulicated cause 
### wasn't clearing buffer, review to make sure i'm getting the right link for right 
### class each time