from src.db_cli.db_handler import DBHandler
import sys
import mysql.connector

def main():
    if(len(sys.argv)<2):
        printUsage()
    else:
        db=DBHandler()

        if(sys.argv[1]=='help'):
            printUsage()
        elif (sys.argv[1]=='create'):
            try:
                rootPasswd,username,password = sys.argv[2:5]
                db.create_new_user(username,rootPasswd,password)
            except mysql.connector.errors.DatabaseError as e:
                print(e)
            except ValueError:
                print('root-password, username, and password are missing')
                printUsage()
                exit()
        elif (sys.argv[1]=='delete'):
            try:
                rootPasswd, username = sys.argv[2:4]
                db.delete_user(rootPasswd,username)
            except mysql.connector.errors.DatabaseError as e:
                print(e)
            except ValueError:
                print('root-password, username are missing.')
                printUsage()
                exit()
        else:
            print(f'{sys.argv[1]} is an invalid command.')
            printUsage()

def printUsage():
    print("Commands available are: 'create <root-password> <username> <password>' 'delete <root-password> <username>' ")

if __name__=="__main__":
    main()
    
