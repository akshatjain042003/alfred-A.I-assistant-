import tabulate


qutting = input("do you want to quit")
while (qutting !="quit"):
    id = input("Enter your username:\t")
    password = input("Enter the password:\t")
    data = [[id,password]]
    head=["USERNAME","PASSWORD"]
    print(tabulate.tabulate(data,headers=head,tablefmt="grid"))






