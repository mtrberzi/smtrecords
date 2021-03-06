#!/usr/bin/env python3

from __future__ import absolute_import

from smtrecords import dbobj, config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import os.path
import hashlib

if config.remotecopy:
    import paramiko

import datetime
import dateutil.parser
import shutil

def read_back_and_confirm(sftp, remotePath, checksum):
    try:
        hasher = hashlib.sha256()
        with sftp.file(remotePath, 'rb') as remoteFile:
            for chunk in iter(lambda: remoteFile.read(4096), b""):
                hasher.update(chunk)
        if checksum != hasher.hexdigest():
            return False
        return True
    except:
        return False

## Entry point

if len(sys.argv) != 4 and len(sys.argv) != 5:
    print("Usage: " + sys.argv[0] + " solvername version /path/to/binary [creation-datetime]")
    sys.exit(1)

solvername = sys.argv[1]
version = sys.argv[2]
solverpath = sys.argv[3]
creationDate = None
if len(sys.argv) == 5:
    creationDate = dateutil.parser.parse(sys.argv[4])
else:
    creationDate = datetime.datetime.utcnow()

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

# if the solver type doesn't already exist, create it
solverClass = session.query(dbobj.Solver).filter(dbobj.Solver.name == solvername).one_or_none()
if solverClass is None:
    solverClass = dbobj.Solver(name=solvername)
    session.add(solverClass)

# check if the named version is already registered
existingVersion = session.query(dbobj.Solver, dbobj.SolverVersion).filter(dbobj.Solver.id == dbobj.SolverVersion.solver_id).filter(dbobj.SolverVersion.version == version).one_or_none()

if existingVersion is not None:
    print("Solver %s-%s already exists." % (solvername, version))
    session.rollback()
    sys.exit(1)

checksum = ""
try:
    with open(solverpath, 'rb') as f:
        hasher = hashlib.sha256()
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
        checksum = hasher.hexdigest()
except Exception as e:
    print("An exception occurred while reading the solver from %s:" % (solverpath,))
    print(e)
    session.rollback()
    sys.exit(1)
print("checksum %s" % (checksum,))

solverFilename = os.path.basename(solverpath)
remoteBaseDir = config.solverbase
remoteSolverDir = remoteBaseDir + "/" + solvername
remoteSolverPath = solvername + "/" + solvername + "-" + version

if config.remotecopy:

    print("Opening connection to %s for file transfer" % (config.remotehost,))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(config.remotehost)
    except Exception as e:
        print("An exception occurred while connecting:")
        print(e)
        session.rollback()
        sys.exit(1)
    sftp = ssh.open_sftp()

    try:
        sftp.stat(remoteSolverDir)
    except FileNotFoundError:
        sftp.mkdir(remoteSolverDir)

    try:
        sftp.put(solverpath, remoteBaseDir + "/" + remoteSolverPath)
        # TODO make remote solver executable
        if not read_back_and_confirm(sftp, remoteBaseDir + "/" + remoteSolverPath, checksum):
            print("Failed to verify solver! Removing file and aborting.")
            try:
                #sftp.remove(remoteBaseDir + "/" + remoteSolverPath)
                pass
            except:
                pass
            sftp.close()
            ssh.close()
            session.rollback()
            sys.exit(1)
    except Exception as e:
        print("Could not copy solver to remote server:")
        print(e)
        sftp.close()
        ssh.close()
        session.rollback()
        sys.exit(1)
    sftp.close()
    ssh.close()
else: # config.remotecopy = False
    dst = os.path.join(remoteBaseDir, remoteSolverPath)
    print("Copying solver to {}".format(dst))
    try:
        os.makedirs(remoteSolverDir, exist_ok=True)
        shutil.copyfile(solverpath, dst)
        mode = os.stat(dst).st_mode
        mode |= (mode & 0o444) >> 2 # copy R bits to X bits
        os.chmod(dst, mode)
    except Exception as e:
        print("Failed to copy solver:")
        print(e)
        session.rollback()
        sys.exit(1)
    
solverVersion = None
if creationDate is None:
    solverVersion = dbobj.SolverVersion(version=version, path=remoteSolverPath, checksum=checksum)
else:
    solverVersion = dbobj.SolverVersion(version=version, path=remoteSolverPath, checksum=checksum, creationdate=creationDate)
solverClass.versions.append(solverVersion)

session.commit()
print("Created solver %s-%s." % (solvername, version))
