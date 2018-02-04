#!/usr/bin/env python3

"""
 *  [2018] Ralph Bellofatto
 *  All Rights Reserved.
 * 
 * NOTICE:  All information contained herein is, and remains
 * the property of Ralph Bellofatto.  
 * The intellectual and technical concepts contained
 * herein are proprietary to Ralph Bellofatto
 * and may be covered by U.S. and Foreign Patents,
 * patents in process, and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material
 * is strictly forbidden unless prior written permission is obtained
 * from Ralph Bellofatto.
 *
 * email: ralph.bellofatto@gmail.com
 *
"""
'''
ptython parser download and unpack debian packages
and resolve package dependendies th3e way that apt get does.
'''


#import signal
import subprocess
import sys
import argparse;
import traceback;
import tempfile;
import os;
import inspect;
import re;
import glob;
import pprint as pp;
import urllib.parse
import urllib.request
import collections;

class ExitError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    

def dbg(self, text):
    print("DEBUG: {}::{}: {}".format(type(self).__name__, inspect.stack()[1][3],text));
    
def whoami(self):
    print("{}::{}".format(type(self).__name__, inspect.stack()[1][3]));

class DebPkg:
    """ package record for an individual packaghe name.
        contained an order dictionary of version numbers.
    """
    def __init__(self):
        self.versions = collections.OrderedDict();
    def __repr__(self):
        return self.__class__.__name__ + ": " + pp.pformat(vars(self))
    
     
    
class DebDb:
    """ PackageDb -- live package db, indexed by package name
                     and version number.
        """
    def __init__(self):
        self.db = collections.OrderedDict();
    def __repr__(self):
        return self.__class__.__name__ + ": " + pp.pformat(vars(self))
    
    def addPackage(self, pkg):
        """ add a package
        """
        # to do more error handling here... maybe...
        pkgName=pkg['Package'];
        pkgVersion=pkg['Version']
        if (not pkgName in self.db):
            p = self.db[pkgName] = DebPkg();
        else:
            p = self.db[pkgName];
        p.versions[pkgVersion] = pkg
        #dbg(self, '{}: version={}'.format(pkgName, pkgVersion))
        
    def getPackage(self, name, version=None):
        """ getPackage -- get the package information dictionary.
            given the package name and an optional version number.
            """
        pass;
    

class AptRepo:
    """ AptRepo container class, contains the raw repo line as well
          as all the information to keep track of each repo.
    """
    def __init__(self, line):
        self.line = ""; # raw repository line.
        self.parseLine(line)
        
    def __repr__(self):
       return self.__class__.__name__ + ": " + pp.pformat(vars(self))
   
    
    def parseLine(self, line):
        self.line = line;     # save this line...
        t = line.split();
        assert len(t) >= 4, 'too few tokens in line: {}'.format(line)
        assert t[0] in ['deb', 'deb-src'], 'invalid type in line: {}'.format(line)
        self.type=t[0];
        self.urlStr=t[1];  
        self.url=urllib.parse.urlparse(self.urlStr) # parsed url..
        self.urlDir=self.url.netloc + self.url.path;
        self.suite=t[2];
        self.components = t[3:];
        #dbg(self, "\n"+pp.pformat(vars(self)))

    def getDistDir(self, arch):
        adir='binary-'+arch;
        if (self.type == 'deb-src'):
            adir='source'
        return(adir)
        
        
    def packagesFile(self, component, arch):
        """ local file name for package
        """
        return(self.urlDir + component + 
               '/' + self.getDistDir(arch) +  
               '/Packages');

    def packagesUrl(self, component, arch):
        """
        full url for Packages file
        """
        return(self.urlStr + 'dists/' + 
               self.suite + '/' + 
               component + '/' + 
               self.getDistDir(arch) + '/Packages')

class AptInstall:
    """ AptInstall
          class to handle all the apt install functions
        """
    def __init__(self,args):
        self.aptRepos = []; # repository list, list of aptRepo
        self.args=args;
        self.debDb = DebDb();
        self.chkCacheDir()
        self.readAptDir()
        
    
    def chkCacheDir(self):
        if (not os.path.isdir(self.args.cache)):
            os.mkdir(self.args.cache)
    
        
    def findAptListFiles(self,aptdir):
        """ findAptListFiles
            locate all list files in the /etc/apt directory
            sources.list AND sources.list.d
            """
        aptListFiles=[aptdir + "/sources.list"];
        sources_list_d=glob.glob(aptdir + "/sources.list.d/*.list")
        aptListFiles.extend(sources_list_d)
        return(aptListFiles)
        
              
    def readAptDir(self):
        """ readAptDir -- read in the etc/apt directory files
              and parse them
            """
        aptListFiles=self.findAptListFiles(self.args.aptdir);
        
        for fname in aptListFiles:
            with open(fname) as f:
                lnum=0;
                for line in f:
                    lnum += 1;
                    line = line.strip()  # remove traiing nl
                    if (line[0] == '#'):   # comment...
                        continue;
                    t = line.split();
                    if (len(t) < 4):      # blank line.
                        continue;
                    #dbg(self,line)
                    if   (t[0] == 'deb') or (t[0] == 'deb-src'):
                        self.aptRepos.append(AptRepo(line))
                    else:
                        raise ExitError('unrecognized line in {}:{}'.format(fname,lnum))
        #dbg(self, "\n" + pp.pformat(self.aptRepos)+'\n')
    
    def update(self):
        """ update -- process the update option
            """
        for r in self.aptRepos:
            #dbg(self, r)
            for c in r.components:
                pkgCache = self.args.cache + '/' + r.packagesFile(c, self.args.arch);
                pkgDir=os.path.dirname(pkgCache)
                pkgUrl = r.packagesUrl(c, self.args.arch);
                print('downloading: {}'.format(pkgUrl));
                if (not os.path.isdir(pkgDir)):  # create the directory if we don't have one...
                    os.makedirs(pkgDir)
                with urllib.request.urlopen(pkgUrl) as f:
                    s=f.read()
                    pkgData=s.decode('utf-8');
                with open(pkgCache, 'w') as f:
                    f.write(pkgData);
                    
    def readPackagesFile(self, filename):
        """ read the repo packages file and store in the packages db.
        """
        lnum=0;
        lastKey=None;
        with open(filename, 'r') as f:
            pkgInfo = {};  # raw package information is just a dictionary
            for line in f:
                lnum += 1;
                if (len(line.strip()) == 0):
                    if (len(pkgInfo) > 0):
                        #dbg(self, pp.pformat(pkgInfo));
                        # todo, put the package info into the proper record
                        self.debDb.addPackage(pkgInfo);
                       
                    lastKey=None;
                    pkgInfo={};   # clear out the previous rec...
                    continue;
                line = line.rstrip();  # remove trailing data.
                if (line[0] == ' '):
                    if (lastKey is not None):
                        pkgInfo[key] = line[1:]
                    continue   # continuation line...
                s=re.search('^(\S+): (.*)$', line);
                if (s is None):
                    s=re.search('^(\S+):.*$', line);
                    if (s == None):
                        dbg(self, "InvalidRecord: {}: {}".format(lnum,line))
                        continue;
                    (key) = s.groups(); value=""
                else:
                    (key, val) = s.groups();
                #dbg(self, pp.pformat(s.groups()))
                pkgInfo[key] = val;

    def install(self):
        """ install -- process the install step
            """
        # check for package directories, if there are any missing, then
        # bail for starters (same as apt-install).... 
        # we may want to make this automatic...
        for r in self.aptRepos:
            #dbg(self, r)
            for c in r.components:
                pkgCache = self.args.cache + '/' + r.packagesFile(c, self.args.arch);
                if (not os.path.exists(pkgCache)):
                    raise ExitError(pkgCache + ' not found, run --update first')
                    
        # second pass, now we parse each pkg file into a master repo directory.
        #   how should w store the packages, keyed (package, packager-ver)
        for r in self.aptRepos:
            #dbg(self, r)
            for c in r.components:
                pkgCache = self.args.cache + '/' + r.packagesFile(c, self.args.arch);
                dbg(self, 'reading: ' + pkgCache)
                self.readPackagesFile(pkgCache)
        #dbg(self, self.debDb)
                

def main():
    parser = argparse.ArgumentParser(description='apt-get install for cross environments ')
    parser.add_argument('-v', '--verbose', 
                        dest='verbose', 
                        help="verbose output", 
                        action='store_true')
    parser.add_argument('-a', '--aptdir', 
                         help="apt director with sources.list and sources.d files", 
                         dest='aptdir',
                         default="etc/apt")
    parser.add_argument('--arch', 
                        dest='arch',
                         help="arch", 
                         default="armhf")
    parser.add_argument('-o', '--outdir', 
                        metavar='"<dir>"', 
                        help='output directory')
    parser.add_argument('-y', '--update', 
                        dest='update', 
                        help="update packages cache", 
                        action='store_true')
    parser.add_argument('-n', '--noinstall', 
                        help="don't install",
                        action='store_true',
                        default=False)
    parser.add_argument('-c', '--cache', 
                        dest='cache',
                         help="cache directory to use", 
                         default="aptcache")

    try:
        args=parser.parse_args(sys.argv[1:])
    except:
        print("argument error:")
        parser.print_help();
        return(1)   

    
    aptInstall=AptInstall(args);
    if (args.update):
        aptInstall.update();
    if (not args.noinstall):
        aptInstall.install();
    
    return(0)
    
if __name__ == '__main__':
    rc=0;
    try:
        rc=main()
        sys.exit(rc)
    except ExitError as e:
        print('(ERROR): {}'.format(e.msg))
    except Exception:  # pylint: disable=W0703
        print("unhandled exception")
        traceback.print_exc();  
        if 'IPython' not in sys.modules:    #just fall through in Ipython, the sys 
            sys.exit(1)                     # exit message is anoying...
    except SystemExit as e:   # keep ipython happy and running
        if 'IPython' in sys.modules:
            if (e.code != 0):
                print('exit: {}'.format(e))
        else:
            exit(e.code)       
        