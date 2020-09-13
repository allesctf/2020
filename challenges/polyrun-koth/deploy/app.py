import subprocess, os
import tempfile
import uuid
import json
import threading
import time
import datetime
import glob
import pathvalidate
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify

UPLOAD_FOLDER = 'tmp'

accepted_teams = {'juniors':{'7wNN52UZmXk38B2l':'polylovers1', 'UShOXsk8kQKkiNjl':'vexillophiles'}, 'seniors':{'0qLdjKWfWtXd3v6b':'Senior A','tboG85o0HDt6CdIf':'Thinking with Poly'}}

# TODO:
# - Secret for Teams?
# - Nice HTML

basecmd1="docker run -it --rm --name my-running-script"
basecmd2=" -v \"$PWD\":/usr/src/myapp -w /usr/src/myapp "

container = {"PHP 7.4":"php:7.4-cli php polyglot",
"Perl 5.20":"perl:5.20 perl polyglot",
"Python 3":"python:3 python polyglot",
"C (gcc4.9)":"gcc:4.9 /bin/bash -c 'gcc -o polyrun polyglot.c && ./polyrun'; rm -f polyrun",
"Ruby 2.5":"ruby:2.5 ruby polyglot",
"Powershell":"mcr.microsoft.com/powershell pwsh polyglot",
"Bash 4.4":"bash:4.4 bash polyglot",
"Erlang (escript)":"erlang escript polyglot",
"Lua 5":"nickblah/lua:5 lua polyglot",
"Coffeescript":"nacyot/coffeescript-coffee:npm coffee polyglot",
"R":"r-base:latest Rscript polyglot",
"Swift":"swift:latest swift polyglot.swift",
"Go 1.13":"golang:1.13 go run polyglot.go",
"Java (openjdk7)":"openjdk:7 /bin/bash -c 'javac Polyglot.java && java Polyglot'; rm -f Polyglot.class",
"Fortran (f95)":"mborges/fortran /bin/bash -c 'f95 polyglot.f95 -o polyrun && ./polyrun'; rm -f polyrun",
"Emojicode":"martingregoire/emojicode /bin/bash -c 'emojicodec -o polyglot.emojib polyglot.emojic && ./polyglot.emojib'",
"Brainfuck":"sergiomtzlosa/brainfuck brainfuck polyglot",
"ADA":"nacyot/ada-gnat:apt /bin/bash -c 'gnatmake -o polyrun polyglot > /dev/null 2>&1 && ./polyrun'; rm -f polyrun",
"Haskell 8.8.3":"haskell:8.8.3 /bin/bash -c 'ghc -o polyrun polyglot.hs > /dev/null 2>&1 && ./polyrun'; rm -f polyrun",
"Cobol":"gregcoleman/docker-cobol /bin/bash -c 'cobc -free -x -o polyrun polyglot  && ./polyrun'; rm -f polyrun"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

def deadThreadKiller(process, timeout, teamID):
    time.sleep(timeout)
    if process.poll() == None:
        p = subprocess.Popen("docker kill my-running-script" + teamID, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Killer Killed")
    

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if 'teamID' not in request.values:
            flash('No Team ID')
            return redirect(request.url)
        teamID = pathvalidate.sanitize_filename(request.values['teamID'])
        if teamID == '': 
            flash('Invalid Team ID')
            return redirect(request.url)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = str(uuid.uuid4())
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            checker = threading.Thread(target=fileRunner, args=(filename, teamID,))
            checker.start()
            teamName="Unknown"
            if teamID in accepted_teams['juniors']:
                teamName=accepted_teams['juniors'][teamID]
            elif teamID in accepted_teams['seniors']:
                teamName=accepted_teams['seniors'][teamID]
            # API to put Record
            return '''
            <!doctype html>
            <head>
            <title>Uploaded file for team {team}</title>
            </head>
            <body>
            <h1>Successfully uploaded file for team {teamN}!</br>Updated results will be shown here in a few seconds: <a href="/check_status?teamID={team}">{teamN}</a>!</h1>
            </body>
            '''.format(team=teamID, teamN=teamName)
    return '''
    <!doctype html>
    <head>
    <title>Upload new file</title>
    </head>
    <body>
    <h1>Upload new file</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file></br></br>
      <label>TeamID:</label>
      <input type=text name=teamID></br></br>
      <input type=submit value=Upload>
    </form>
    <div>
    <h2>Available interpreters:</h2>
    <p>ADA, Emojicode, Perl 5.20, C (gcc4.9), Ruby 2.5, Powershell, Bash 4.4, Erlang (escript), Lua 5, PHP 7.4, Coffeescript, R, Swift, Go 1.13, Java (openjdk7), Fortran (f95), Brainfuck, Haskell 8.8.3, Python 3, Cobol</p>
    </div>
    </body>
    '''

@app.route('/check_status', methods=['GET'])
def check_status():
    if "teamID" in request.args:
        teamID = request.args.get("teamID")
        if teamID in accepted_teams['juniors'].values():
            for a,b in accepted_teams['juniors'].items():
                if teamID == b:
                    teamID = a
        elif teamID in accepted_teams['seniors'].values():
            for a,b in accepted_teams['seniors'].items():
                if teamID == b:
                    teamID = a

        if not os.path.exists(str(teamID) + "_results.txt"):
            return '''
            <!doctype html>
            <head>
            <title>Team does not exist or did not submit a file yet</title>
            </head>
            <body>
            <h1>Team does not exist or did not submit a file yet (in case of 2, please refresh in a few seconds)</h1>
            </body>
            '''
        else:
            json_file = open(str(teamID) + "_results.txt", "r")
            data = json.load(json_file)
            teamName="Unknown"
            if teamID in accepted_teams['juniors']:
                teamName=accepted_teams['juniors'][teamID]
            elif teamID in accepted_teams['seniors']:
                teamName=accepted_teams['seniors'][teamID]
            return '''
            <!doctype html>
            <head>
            <title>Uploaded file for team {teamN}</title>
            </head>
            <body>
            <h1>Current and best results for team {teamN}:</h1>
            <p><h2>Points for last uploaded file ({cur_time}): {cur_count}</h2>
            <h2>Results:</h2>
            {cur_result}</p>
            <p><h2>Points for best uploaded file ({best_time}): {best_count}</h2>
            <h2>Results:</h2>
            {best_result}</p>
            </body>
            '''.format(team=teamID, teamN=teamName, cur_count=data["current"]["count"], cur_result=data["current"]["results"], cur_time=data["current"]["timestamp"], best_time=data["best"]["timestamp"], best_count=data["best"]["count"], best_result=data["best"]["results"])
    else:
        teams = [a.replace("_results.txt","") for a in os.listdir(".") if "_results.txt" in a]
        for i,t in enumerate(teams):
            if t in accepted_teams['juniors']:
                teams[i]=accepted_teams['juniors'][t]
            elif t in accepted_teams['seniors']:
                teams[i]=accepted_teams['seniors'][t]
        return render_template("list_teams.html", data=teams)

@app.route('/get_scores', methods=['GET'])
def get_scores():
    secret = request.args.get('secret', default = 1)
    cat = request.args.get('category', default = 0)
    if not isinstance(cat, int):
        if cat.isdigit():
            cat = int(cat)
        else :
            return "Nope"
    if secret != "dcf00885323e62c0629380dc76fbfaa9":
        return "Nope"
    resp = []
    for team in glob.glob('*_results.txt'):
        json_file = open(team, "r")
        data = json.load(json_file)
        json_file.close()
        if cat == 0 and data["teamID"] in  accepted_teams['juniors'].keys():
            resp.append({"team":accepted_teams['juniors'][data["teamID"]],"points":data["best"]["count"],"additionalData":data["best"]["results"]})
        elif cat == 1 and data["teamID"] in  accepted_teams['seniors'].keys():
            resp.append({"team":accepted_teams['seniors'][data["teamID"]],"points":data["best"]["count"],"additionalData":data["best"]["results"]})
    return jsonify(resp)
    

def fileRunner(filename, teamID):
    counter = 0
    results = ""
    testFile = open(app.config['UPLOAD_FOLDER'] + "/" + filename,"rb").read()
    with tempfile.TemporaryDirectory(dir="/tmp") as testDir:
        testFile2 = open(testDir + "/polyglot","wb")
        testFile3 = open(testDir + "/polyglot.c","wb")
        testFile4 = open(testDir + "/polyglot.f95","wb")
        testFile5 = open(testDir + "/polyglot.emojic","wb")
        testFile6 = open(testDir + "/polyglot.swift","wb")
        testFile7 = open(testDir + "/polyglot.go","wb")
        testFile8 = open(testDir + "/Polyglot.java","wb")
        testFile9 = open(testDir + "/polyglot.hs","wb")
        testFile2.write(testFile)
        testFile3.write(testFile)
        testFile4.write(testFile)
        testFile5.write(testFile)
        testFile6.write(testFile)
        testFile7.write(testFile)
        testFile8.write(testFile)
        testFile9.write(testFile)
        testFile9.close()
        testFile8.close()
        testFile7.close()
        testFile6.close()
        testFile5.close()
        testFile4.close()
        testFile3.close()
        testFile2.close()
        for lang in container:
            result = ""
            resultErr = ""
            addPoints = 0
            try:
                p = subprocess.Popen(basecmd1 + teamID + basecmd2 + container[lang], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=testDir)
                killer = threading.Thread(target=deadThreadKiller, args=(p, 5, teamID,))
                killer.start()
                result, resultErr = p.communicate()
            except Exception as e:
                resultErr = str(e.output)
                #print("Got Error: " + str(e.output))
            if "try harder" in str(result) and "error" not in str(result).lower() and "correct" not in str(result).lower():
                if "try harder" == result.decode("utf-8") :
                    addPoints = 3
                else:
                    addPoints = 2
                counter += addPoints
                results += lang + ": success (" + str(addPoints) + ")</br>"
            elif "try harder" in str(resultErr) or "try harder" in str(result):
                addPoints = 1
                counter += addPoints
                results += lang + ": success (" + str(addPoints) + ")</br>"
            else:
                results += lang + ": error</br>"
            print(lang + ": " + str(result))

    data = {}
    curtime = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
    if os.path.isfile(str(teamID) + "_results.txt"):
        json_file = open(str(teamID) + "_results.txt", "r")
        data = json.load(json_file)
        json_file.close()
        
        data["current"]["count"] = counter
        data["current"]["results"] = results
        data["current"]["timestamp"] = curtime
        data["teamID"] = str(teamID)
        if data["best"]["count"] < counter:
            data["best"]["count"] = counter
            data["best"]["results"] = results
            data["best"]["timestamp"] = curtime
    else:
        data["current"] = {"count":counter, "results":results, "timestamp":curtime}
        data["best"] = {"count":counter, "results":results, "timestamp":curtime}
        data["teamID"] = str(teamID)
    json_file = open(str(teamID) + "_results.txt", "w")
    json.dump(data, json_file)
    json_file.close()

