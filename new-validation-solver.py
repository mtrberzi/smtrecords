#!/usr/bin/env python3

import dbobj
import config

import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
import os
import os.path
import hashlib
import paramiko

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

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " solver-name /path/to/binary")
    sys.exit(1)

solvername = sys.argv[1]
solverpath = sys.argv[2]

engine = dbobj.mk_engine()
Session = sessionmaker(bind=engine)
session = Session()

# check if the named validation solver is already registered

existingVersion = session.query(dbobj.ValidationSolver).filter(dbobj.ValidationSolver.name == solvername).one_or_none()

if existingVersion is not None:
    print("Validation solver {} already exists.".format(solvername))
    session.rollback()
    sys.exit(0)

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

# path is a relative path
vSolverEntry = dbobj.ValidationSolver(name=solvername, path=solvername, checksum=checksum)
remoteFilename = os.path.join(config.validationsolverbase, solvername)

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
    # create validation solver directory if it doesn't exist
    try:
        sftp.stat(config.validationsolverbase)
    except FileNotFoundError:
        sftp.mkdir(config.validationsolverbase)
    # copy validation solver and verify
    try:
        sftp.put(solverpath, remoteFilename)
        if not read_back_and_confirm(sftp, remoteFilename, checksum):
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
else:
    raise Exception("not implemented yet")

session.add(vSolverEntry)
session.commit()
print("Created solver {}.".format(solvername))
