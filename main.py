import mysql.connector, bcrypt
import getpass, pyperclip
import random, string
from time import sleep
import tabulate

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password=''
    for i in range(length):
        password += ''.join(random.choice(characters))
    return password

def show_menu(name,uid,cursor,connection):
    print("Welcome ",name)
    y='y'
    while y in "yY":
        choice = int(input("CLI PASSWORD MANAGER\n1\tview saved passwords\n2\tadd new entry\n3\tedit saved passwords\n4\trandom password generater\n5\tdelete saved entry\n6\tedit account deatils\n7\tdelete account\n0\texit\nchoose one option : "))
        match choice:
            case 0:
                print("bie!")
                y='n'
            case 1:
                query="SELECT website,login,password FROM passwords WHERE userid = %s"
                cursor.execute(query,(uid,))
                data=cursor.fetchall()
                if cursor.rowcount==0:
                    print("no saved passwords found\n")
                else:
                    print("SAVED PASSWORDS")
                    print("ID\tWEBSITE")
                    for i in range(cursor.rowcount):
                        print(i,"\t",data[i][0])
                    pid=int(input("choose one option : "))
                    print("website \t",data[pid][0])
                    print("login   \t",data[pid][1])
                    pyperclip.copy(data[pid][2])
                    print("password\t [copied to clipboard]")
                    x=input("do you need to view your password (y/n) : ")
                    if x.lower()=='y':
                        print("password \t",data[pid][2],"\n")
                        sleep(5)
                    else:
                        y='y'
            case 2:
                print("ADD NEW ENTRY")
                website=input("enter website : ")
                login=input("enter login : ")
                c=input("generate random password (y/n) : ")
                if c in 'yY':
                    password=generate_password()
                    pyperclip.copy(password)
                    print('password copied to clipboard')
                else:
                    password=input("enter password : ")
                query="INSERT INTO passwords (userid, website, login, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(query,(uid, website, login, password))
                connection.commit()
                print("entry added successfully\n")
                sleep(3)
            case 3:
                print("EDIT SAVED PASSWORDS")
                query="SELECT uid,website,login,password FROM passwords WHERE userid = %s"
                cursor.execute(query,(uid,))
                data=cursor.fetchall()
                if cursor.rowcount==0:
                    print("no saved passwords found\n")
                else:
                    L=[]
                    tab=[]
                    for i in range(cursor.rowcount):
                        tab.append([data[i][0],data[i][1],data[i][2]])
                        L.append(data[i][0])
                    print(tabulate.tabulate(tab, headers=["UID","WEBSITE", "LOGIN"]))
                    pid=int(input("enter uid to edit details : "))
                    if pid in L:
                        cid=int(input("\n1\twebsite\n2\tlogin\n3\tpassword\nchoose one option to edit : "))
                        match cid:
                            case 1:
                                website = input("enter new website : ")
                                query="UPDATE passwords SET website = %s WHERE uid = %s"
                                cursor.execute(query,(website, pid))
                                connection.commit()
                                print("website changed successfully\n")
                            case 2:
                                login = input("enter new login : ")
                                query="UPDATE passwords SET login = %s WHERE uid = %s"
                                cursor.execute(query,(login, pid))
                                connection.commit()
                                print("login changed successfully\n")
                            case 3:
                                c=input("generate random password (y/n) : ")
                                if c in 'yY':
                                    password=generate_password()
                                    pyperclip.copy(password)
                                    print('password copied to clipboard')
                                else:
                                    password=input("enter password : ")
                                query="UPDATE passwords SET password = %s WHERE uid = %s"
                                cursor.execute(query,(password, pid))
                                connection.commit()
                                print("password changed successfully\n")
                            case _:
                                print("invalid choice")
                    else:
                        print("you don't have permission to do so")
                    sleep(3)
            case 4:
                print("RANDOM PASSWORD GENERATOR")
                password = generate_password()
                pyperclip.copy(password)
                print("a random password is copied to clipboard\n")
                sleep(2)
            case 5:
                print("DELETE SAVED ENTRY")
                query="SELECT uid,website,login FROM passwords WHERE userid = %s"
                cursor.execute(query,(uid,))
                data=cursor.fetchall()
                if cursor.rowcount==0:
                    print("no saved passwords found")
                else:
                    L=[]
                    #tab=[]
                    for i in range(cursor.rowcount):
                        #tab.append([data[i][0],data[i][1],data[i][2]])
                        L.append(data[i][0])
                    print(tabulate.tabulate(data, headers=["UID","WEBSITE", "LOGIN"]))
                    pid=int(input("choose one option : "))
                    pid2=int(input("re-enter to confirm : "))
                    if pid != pid2:
                        print("options does not match, try again\n")
                        y='y'
                    else:
                        if pid in L:
                            query="DELETE FROM passwords WHERE uid = %s"
                            cursor.execute(query,(pid,))
                            connection.commit()
                            print("password deleted successfully!\n")
                        else:
                            print("you don't have permission to do so\n")
                sleep(3)
            case 6:
                print("EDIT ACCOUNT DETAILS")
                query = "SELECT email,name,master_password FROM users WHERE uid = %s"
                cursor.execute(query,(pid,))
                result = cursor.fetchone()
                cp=input("enter current password : ")
                if verify_password(result[2], cp):
                    print("current email : ",result[0])
                    print("current name : ",result[1])
                    cid=int(input("\n1\tlogin email\n2\taccount name\n3\tchange password\nchoose one option to edit : "))
                    match cid:
                        case 1:
                            newemail=input("enter new email : ")
                            query = "SELECT COUNT(*) FROM users WHERE email = %s AND uid != %s"
                            cursor.execute(query,(newemail.lower(), uid))
                            email_count = cursor.fetchone()[0]
                            if email_count > 0:
                                print("user already exists with the email address\n")
                            else:
                                query="UPDATE users SET email = %s WHERE uid = %s"
                                cursor.execute(query,(newemail.lower(), uid))
                                connection.commit()
                                print("email changed successfully\n")
                        case 2:
                            newname=input("enter new name : ")
                            query="UPDATE users SET name = %s WHERE uid = %s"
                            cursor.execute(query,(newname, uid))
                            connection.commit()
                            print("name changed successfully\n")
                        case 3:
                            print("!!REMEBER YOU CANNOT RECOVER YOUR ACCOUNT IF YOU FORGET THE MASTER PASSWORD!!")
                            np=input("enter new password : ")
                            np2=input("re-enter password : ")
                            if np == np2:
                                query="UPDATE users SET master_password = %s"
                                cursor.execute(query,(hash_password(np).decode('utf-8'),))
                                connection.commit()
                                print("Password changed successfully\n")
                            else:
                                print("passwords does not match\n")
                        case _:
                            print("invalid choice\n")
                else:
                    print("incorrect password\n")
                sleep(3)
            case 7:
                print("DELETE ACCOUNT")
                query = "SELECT master_password FROM users WHERE uid = %s"
                cursor.execute(query,(uid,))
                result = cursor.fetchone()
                print("!! WARNING THIS CANNOT BE UNDONE !!")
                cp=input("enter current password : ")
                if verify_password(result[0], cp):
                    confirm=input("type 'yes' to confirm : ")
                    if confirm.lower() == 'yes':
                        query="SELECT COUNT(*) FROM passwords WHERE userid = %s"
                        cursor.execute(query,(uid,))
                        if cursor.fetchone()[0] > 0:
                            query="DELETE FROM passwords WHERE userid = %s"
                            cursor.execute(query,(uid,))
                        query="DELETE FROM users WHERE uid=%s"
                        cursor.execute(query,(uid,))
                        connection.commit()
                        print("account deleted")
                        break
                else:
                    print("incorrect password")
            case _:
                print("invalid option")

def main():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='password', database='passwd_manager')
    if connection.is_connected():
        cursor = connection.cursor()
        query="CREATE TABLE IF NOT EXISTS users(uid INT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), master_password VARCHAR(255))"
        cursor.execute(query)
        query="CREATE TABLE IF NOT EXISTS passwords(uid INT PRIMARY KEY, userid INT, website VARCHAR(255), login VARCHAR(255), password VARCHAR(255), FOREIGN KEY (userid) REFERENCES users(uid))"
        cursor.execute(query)
        connection.commit()
        print("Welcome to password manager")
        email = input("enter login email : ")
        query = "SELECT master_password,name,uid FROM users WHERE email = %s"
        cursor.execute(query,(email.lower(),))
        result = cursor.fetchone()
        if cursor.rowcount == 0:
            print("email does not exist. Would you like to create a new account?")
            create_account = input("enter 'yes' or 'no': ")
            if create_account.lower() == "yes":
                name = input("enter your name: ")
                print("!!REMEBER YOU CANNOT RECOVER YOUR ACCOUNT IF YOU FORGET THE MASTER PASSWORD!!")
                master_password = input("enter your master password: ")
                master_password2=input("re-enter password : ")
                if master_password == master_password2:
                    hashed_password = hash_password(master_password)
                    query = "INSERT INTO users (name, email, master_password) VALUES (%s, %s, %s)"
                    cursor.execute(query,(name, email.lower(), hashed_password.decode('utf-8')))
                    connection.commit()
                    print("account created successfully!")
                else:
                    print("passwords does not match")
            else:
                print("bie.")
        else:
            mainpass = getpass.getpass("enter master password : ")

            if result and verify_password(result[0], mainpass):
                show_menu(result[1],result[2],cursor,connection)
            else:
                print("incorrect password")
        connection.close()
    else:
        print("Could not connect to database")
try:
    main()
except Exception as e:
    print("error occured :",e)
    print("restarting program completely...\n")
    sleep(5)
    main()
    
