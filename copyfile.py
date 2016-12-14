"""
How to use this? 
set the host_path and a dest_path
create a .txt file at the same directory.
Emjoy it!


sentan. 2016
"""
import pysftp
import sys
import getpass
import paramiko
import socket

#####################################
## Fill up your information at here!!
#####################################
host_path = r'/home/sentan/Documents/python_local'
host_path_dir = r'/home/sentan/Documents/python_local/local'
dest_path = r'/usr/autoprog/'
dest_path_dir = r'/usr/autoprog/local'
file_to_read = ['tester']
####################################

username = raw_input('Please enter your username: ')
if not username:
    username = getpass.getuser()

for retry in xrange(3):
    password = getpass.getpass('Password: ')
    if password:
        print 'logged in'
        break
    else:
        continue
else:
    print 'Max retry. Aborting'
    exit(0)

print '********************'
print 'WELCOME, {}\n'.format(username)
print 'At {}({})'.format(socket.gethostname(),socket.gethostbyname(socket.gethostname()))
print '********************'

failed_tester = []
station_list = []
file_list = []
e = ''

print 'Program started!!!'

for file_read in file_to_read:
    try:
        print 'opening file {}.txt'.format(file_read)
        f = open('{}.txt'.format(file_read), 'r')
        f = f.read()
    except:
        print 'Not able to get the tester list'
        print 'Aborting this program'
        exit(0)

    for i in f.splitlines():
        if 'end' not in i:
            if 'tester' in file_read:
                station_list.append(i)
            elif '#' in file_read:
                continue
            else:
                file_list.append(i)
        else:
            print 'EOF detected.'
            break

print 'Done reading station list..\nPreparing for the copying'

for index, test_station in enumerate(station_list):
    try:
        with pysftp.Connection('{}'.format(test_station), username=username, password=password) as sftp:
            if sftp.isdir(dest_path_dir):
                print 'changing directory access first...'
                print '{}'.format(sftp.listdir(dest_path))
                result = sftp.execute('chmod -R 777 {}'.format(dest_path_dir))
                if not result:
                    print 'File accesss privillege set.'
                    print 'Removing the old files'
                    result = sftp.execute('rm -r {}'.format(dest_path_dir))
                    if not result:
                        print 'Updating the directory with new files'
                        sftp.put_r(host_path, dest_path, True, True)
                    else:
                        print 'Not able to patch with new files'
                        print 'Break out'
                        failed_tester.append(test_station)
                        result = ''
                else:
                    print 'Not able to change the permission, breaking out ...'
                    failed_tester.append(test_station)
                    result = ''
            else:
                print 'copying file ...'
                sftp.put_r(host_path, dest_path, True, True)
                sftp.close()
    except IOError as e:
        failed_tester.append(test_station)
        print '{} copying failed.'.format(test_station),
        print 'destination problem, please use check on the target path UID & Permission\n'
    except OSError as e:
        failed_tester.append(test_station)
        print '{} copying failed.\n'.format(test_station),
        print 'Local path doesn\'t exist'
    except paramiko.ssh_exception.AuthenticationException as e:
        print 'Wrong password! Rilek. Retry !!!'
        break
    except paramiko.ssh_exception.SSHException as e:
	print 'The target tester down! Please context te.'
        failed_tester.append(test_station)
    except:
        e = 'unknown error' 
        print 'Unexpected Error! {}'.format(sys.exc_info()[0])
        print 'I am failing now but I can\'t think of any error now'
        break
    finally:
        if not e:
            with pysftp.Connection('{}'.format(test_station), username=username, password=password) as sftp:
                sftp.cd(dest_path)
                print 'changing directory access ...'
                # result = sftp.execute('rm -r {}'.format(dest_path_dir))
                result = sftp.execute('chmod -R 777 {}'.format(dest_path_dir))
                if not result:
                    print 'File accesss privillege set.'
                else:
                    print 'Not able to change the permission'
                    failed_tester.append(test_station)
                print 'Done copying for {}'.format(test_station)
                print 'Closing connection for {}\n'.format(test_station)
                print 'Progress {} of {} ...'.format((index + 1), len(station_list))
                result = ''
                sftp.close()
        else:
            print e
            print 'Error found! Aborting the copying.'
            print sys.exc_info()[0]
            e = ''
else:
    print 'Program Done, Retrieving report\n'

failed_tester = list(set(failed_tester))

if failed_tester:
    print 'Tester which failed {}\n'.format(len(failed_tester))
    print 'Failing testers: {}\n'.format(failed_tester)
else:
    print 'Completed for all tester\n'
    print 'All files are copied successfully\n'
