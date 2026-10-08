import customtkinter as ctk
from tkinter import messagebox,ttk
from tkinter import *
import pandas as pd
from datetime import datetime
import json



root = ctk.CTk()
ctk.set_appearance_mode('system')
root.geometry("1000x750+300+50")
root.title("Vehicle Rental System")
ctk.CTkLabel(root,text="Vehicle Rental Management System", font =('Arial', 22 ,'bold')).pack(pady = 15)

#user-vehicle,rented,calc

CSV_File = "bikes.csv"
RENTED_CSV = 'rented_vehicle.csv'


def search(dashboard,dataframe):

    global table_frame,filter_frame,df

    # ---------- Load CSV ----------
    def load_csv():
        global df
        try:
            return pd.read_csv(dataframe)
        except FileNotFoundError:
            messagebox.showerror(f"{CSV_File} not Found", f"{CSV_File} not Found, please check again !!")
            return pd.DataFrame()

    df = load_csv()

    # ---------- Clear existing widgets ----------
    for widget in dashboard.winfo_children():
        widget.destroy()

    # ---------- Title ----------
    title = ctk.CTkLabel(dashboard, text="Search Entry", font=("Arial", 24, "bold"))
    title.pack(pady=10)

    # ---------- Filter Section ----------
    filter_frame = ctk.CTkFrame(dashboard)
    filter_frame.pack(pady=5)

    search_entry = ctk.StringVar()
    search_field = ctk.CTkEntry(filter_frame, textvariable=search_entry, width=250,height=30)
    search_field.pack(side=LEFT, padx=5)

    # ---------- Table Frame ----------
    table_frame = ctk.CTkFrame(dashboard)
    table_frame.pack(fill="both", expand=True, pady=10, padx=10)

    # ---------- Table Functions ----------
    def load_table(dataframe):
        global tree

        for widget in table_frame.winfo_children():
            widget.destroy()

        tree_scroll = ctk.CTkScrollbar(table_frame)
        tree_scroll.pack(side='right', fill='y')

        tree_x_scroll = ctk.CTkScrollbar(table_frame,orientation='horizontal')
        tree_x_scroll.pack(side = "bottom",fill='x')

        cols = list(dataframe.columns)
        tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                            yscrollcommand=tree_scroll.set,xscrollcommand=tree_x_scroll.set, selectmode="extended")
        tree_scroll.configure(command=tree.yview)
        tree_x_scroll.configure(command=tree.xview)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        tree.tag_configure('oddRow', background="white")
        tree.tag_configure('evenRow', background="lightblue")

        for i, (_, row) in enumerate(dataframe.iterrows()):
            tag = 'evenRow' if i % 2 == 0 else 'oddRow'
            tree.insert("", "end", values=list(row), tags=(tag,))

    def filter_table():
        query = search_entry.get().lower()
        if query == "":
            load_table(df)
            return
        filtered = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]

        load_table(filtered)

    def clear():
        search_entry.set("")
        load_table(df)


    # ---------- Buttons ----------
    ctk.CTkButton(filter_frame, text="Search", command=filter_table,height=30).pack(side=LEFT, padx=5)
    ctk.CTkButton(filter_frame, text="Clear", command=clear,height=30).pack(side=LEFT, padx=5)



    # ---------- Table Style ----------
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="#D3D3D3",
        foreground="black",
        rowheight=40,
        fieldbackground="#D3D3D3",
        font=("Roboto", 12, "bold")
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 13, "bold"),
        background="#2E8B57",
        foreground="white",
        padding=(10, 5),
        borderwidth=1,
        relief="raised",
    )

    style.map(
        "Treeview.Heading",
        background=[('active', '#3CB371')],
        relief=[('pressed', 'groove')]
    )

    style.map('Treeview', background=[("selected", '#347083')])

    # ---------- Load initial data ----------
    tree = None
    load_table(df)


#####Login Page######

def login():

    global user_index
    login_type = segment_menu.get()
    username = user_entry.get()
    password = pass_entry.get()

    if not username or not password:
        messagebox.showerror("Login Error", "Username and Password cannot be empty.")
        return

    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messagebox.showerror("Login Error", "Credential file (data.json) not found or is corrupted.")
        return

    if login_type == 'Admin':
        for admin_user in data['admin']:
            if admin_user['username'] == username and admin_user['password'] == password:
                messagebox.showinfo("Login Success", "Welcome, Admin!")
                admin()  # Call the admin dashboard function
                return
        messagebox.showerror("Login Failed", "Invalid Admin credentials.")

    elif login_type == 'User':
        for index, user_creds in enumerate(data['user']):
            if user_creds['username'] == username and user_creds['password'] == password:
                user_index = index  # Store user's index to get their name later
                messagebox.showinfo("Login Success", f"Welcome, {user_creds['name']}!")
                user()  # Call the user dashboard function
                return
        messagebox.showerror("Login Failed", "Invalid User credentials.")


###main###
def main():
    global user_entry,pass_entry,segment_menu,login_frame

    login_frame = ctk.CTkFrame(root, corner_radius=15, border_width=2)
    login_frame.pack(padx=50, pady=50, fill="both", expand=True)

    ctk.CTkLabel(login_frame, text="Login Page", font=("Roboto", 22, "bold")).pack(pady=12)

    segment_menu = ctk.CTkSegmentedButton(login_frame, values=["Admin", "User"])
    segment_menu.set("User")
    segment_menu.pack(padx=20, pady=30, ipadx=20, ipady=5)


    user_entry = ctk.CTkEntry(login_frame, placeholder_text="Username", width=300, height=40)
    user_entry.pack(pady=15)

    pass_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", width=300, height=40, show='*')
    pass_entry.pack(pady=15)

    login_btn = ctk.CTkButton(login_frame, text="Login", width=200, height=40, command=login)
    login_btn.pack(pady=30)


    root.mainloop()


def add_new_user():
    for widget in home_frame.winfo_children():
        widget.destroy()

    def new_user_added():
        new_user = {
            "username": new_user_username.get(),
            "password": new_user_password.get()
        }

        try:
            with open('data.json', 'r') as fr:
                data = json.load(fr)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"user": []}

        data["user"].append(new_user)

        with open('data.json', 'w') as fw:
            json.dump(data, fw, indent=4)

        new_user_top.destroy()
        messagebox.showinfo("New User Added","New User Added Successfully!")

    new_user_top = ctk.CTkToplevel(root)
    new_user_top.geometry('450x400')

    ctk.CTkLabel(new_user_top, text="New User Entry", font=('Arial', 24, 'bold')).pack(padx=5,pady=20)
    new_user_username = ctk.CTkEntry(new_user_top, placeholder_text="Username", width=300, height=40)
    new_user_username.pack(pady=20)

    new_user_password = ctk.CTkEntry(new_user_top, placeholder_text="Password", width=300, height=40, show="*")
    new_user_password.pack(pady=20)

    ctk.CTkButton(new_user_top, text="Add User", command=new_user_added).pack(pady=20,ipadx= 5,ipady = 5)



###Home###
def Home():
    global home_frame

    for widget in dashboard.winfo_children():
        widget.destroy()

    ctk.CTkLabel(dashboard, text="Home Dashboard", font=('Arial', 22, 'bold')).pack(padx=5, pady=10)

    now = datetime.now()

    # --- Load Data ---
    data = pd.read_csv(RENTED_CSV)
    all_bikes = pd.read_csv(CSV_File)

    home_frame = ctk.CTkFrame(dashboard, border_width=2, fg_color='#272757')
    home_frame.pack(padx=20, pady=20, expand=True, fill='both')

    # -------- TOP STATS SECTION --------
    stats_frame = ctk.CTkFrame(home_frame, border_width=0, fg_color="transparent")
    stats_frame.pack(side='top', fill='x', padx=10, pady=10)

    # Total Rented
    total_rented_frame = ctk.CTkFrame(stats_frame, border_width=2, fg_color='#8686AC')
    total_rented_frame.pack(side='left', anchor='nw', padx=20, pady=20, ipadx=30, ipady=25, expand=True, fill='both')

    ctk.CTkLabel(total_rented_frame, text="Total Rented Bikes", font=('Arial', 24, 'bold')).pack(pady=12)
    ctk.CTkLabel(total_rented_frame, text=str(len(data)), font=('Arial', 24, 'bold')).pack(pady=12)

    # Today Rented
    today_rented = data[data['date'] == now.date().strftime("%Y-%m-%d")]

    today_rented_frame = ctk.CTkFrame(stats_frame, border_width=2, fg_color='#8686AC')
    today_rented_frame.pack(side='left', anchor='ne', padx=20, pady=20, ipadx=30, ipady=25, expand=True, fill='both')

    ctk.CTkLabel(today_rented_frame, text="Today Rented Bikes", font=('Arial', 24, 'bold')).pack(pady=12)
    ctk.CTkLabel(today_rented_frame, text=str(len(today_rented)), font=('Arial', 24, 'bold')).pack(pady=12)


    # -------- PLOT SECTION --------
    plot_frame = ctk.CTkFrame(home_frame, border_width=2)
    plot_frame.pack(side='bottom', expand=True, fill='both', padx=30, pady=10)

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt

    # Values for pie chart
    today_count = len(today_rented)
    rented_before = len(data) - today_count
    total_bikes = len(all_bikes)
    available_bikes = total_bikes - len(data)

    sizes = [today_count, rented_before, available_bikes]
    labels = ["Rented Today", "Previously Rented", "Available Bikes"]
    explode = [0.1, 0.05, 0]

    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(sizes, labels=labels,
                   autopct='%1.1f%%',
                    explode=explode,
                    startangle=90
           )
    ax.set_title("Bike Rental Overview")

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill='both')

    # -------- ADD USER BUTTON --------

    exists = any(isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Add User"
                 for widget in sideBar.winfo_children())

    if not exists:
        add_user = ctk.CTkButton(sideBar, text="Add User", command=add_new_user)
        add_user.pack(side='bottom', pady=20, ipadx=5, ipady=5)


def add_new_bike():
    global bike_name,model,bike_engine,bike_gear_type,bike_model_year,functionalities
    for widget in dashboard.winfo_children():
        widget.destroy()

    functionalities = [
        ("name", "Enter Bike Name"),
        ("model", "Bike Model"),
        ("bike_engine", "Bike Engine Power"),
        ("bike_gear_type", "Bike Gear Type"),
        ("bike_model_year","Bike Model Year")
    ]

    add_new_bike_frame = ctk.CTkFrame(dashboard, corner_radius=15, border_width=2)
    add_new_bike_frame.pack(padx=50, pady=50, fill="both", expand=True)

    ctk.CTkLabel(add_new_bike_frame, text="Add New Bike", font=("Roboto", 22, "bold")).pack(pady=12)

    bike_name = ctk.CTkEntry(add_new_bike_frame, placeholder_text="Enter Bike Name", width = 300, height = 40)
    bike_name.pack(pady=15)

    model = ctk.CTkEntry(add_new_bike_frame, placeholder_text="Bike Model", width = 300, height = 40)
    model.pack(pady=15)

    bike_engine = ctk.CTkEntry(add_new_bike_frame, placeholder_text="Bike Engine Power", width = 300, height = 40)
    bike_engine.pack(pady=15)

    bike_gear_type = ctk.CTkEntry(add_new_bike_frame, placeholder_text="Bike Gear Type", width = 300, height = 40)
    bike_gear_type.pack(pady=15)

    bike_model_year = ctk.CTkEntry(add_new_bike_frame, placeholder_text="Bike Model Year", width = 300, height = 40)
    bike_model_year.pack(pady=15)

    rate_per_hr = ctk.CTkEntry(add_new_bike_frame,placeholder_text="Rate Per Hour",width= 300,height= 40)
    rate_per_hr.pack(pady = 15)



    def add_new_bike_1():
        now = datetime.now()

        # Load existing bikes CSV
        try:
            bikes_df = pd.read_csv(CSV_File)
        except FileNotFoundError:
            bikes_df = pd.DataFrame(
                columns=["id", "bike_name", "model", "engine", "gear_type", "model_year", "rate_per_hour"])


        if not bikes_df.empty:
            new_id = bikes_df['id'].max() + 1
        else:
            new_id = 1

        # Create new bike row
        new_bike = {
            "id": new_id,
            "name": bike_name.get(),
            "model": model.get(),
            "engine": bike_engine.get(),
            "gear_type": bike_gear_type.get(),
            "model_year": bike_model_year.get(),
            "rate_per_hour": rate_per_hr.get()
        }

        # Append to dataframe and save
        bikes_df = pd.concat([bikes_df, pd.DataFrame([new_bike])], ignore_index=True)
        bikes_df.to_csv(CSV_File, index=False)

        messagebox.showinfo("Bike Added", f"New bike '{bike_name.get()}' added with ID {new_id}!")

        # Clear fields
        bike_name.delete(0, "end")
        model.delete(0, "end")
        bike_engine.delete(0, "end")
        bike_gear_type.delete(0, "end")
        bike_model_year.delete(0, "end")
        rate_per_hr.delete(0, "end")

    ctk.CTkButton(add_new_bike_frame,command=add_new_bike_1,text ="Add Bike").pack(pady = 10,ipadx = 5,ipady=5)


def calc_rent_func():

    calc_rent_top = ctk.CTkToplevel(root)
    calc_rent_top.geometry("550x650+300+50")

    try:
        selected = tree.item(tree.focus(), 'values')
        if not selected:
            messagebox.showerror("Error", "Please select a rented vehicle first.")
            return
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching selection: {e}")
        return



    def calc_rent_func_final():
        global pd
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        rented = pd.read_csv(RENTED_CSV)

        for i in range(len(rented)):
            if rented.loc[i, 'status'] != 'Returned':
                rented.loc[i, 'return'] = today_date
                rented.loc[i, 'ret_time'] = current_time
                rented.loc[i, 'status'] = 'Returned'

        rented.to_csv(RENTED_CSV, index=False)
        print("CSV updated successfully.")


        def add_row_to_csv(selected):
            """
            Adds a row to the CSV based on the 'selected' list and sorts by id.
            """

            row_dict = {
                'id': int(selected[0]),  # ensure id is int
                'name': selected[5],
                'model': selected[6],
                'engine': selected[7],
                'gear_type': selected[8],
                'model_year': selected[9],
                'rate_per_hour': selected[15]
            }

            try:
                dtf = pd.read_csv(CSV_File)
            except FileNotFoundError:
                dtf = pd.DataFrame(columns=row_dict.keys())

            # Convert 'id' column to int to avoid sorting errors
            if not dtf.empty:
                dtf['id'] = dtf['id'].astype(int)

            # Convert row_dict to DataFrame and concatenate

            new_row_df = pd.DataFrame([row_dict])
            if new_row_df['id'].iloc[0] not in dtf['id'].values:
                dtf = pd.concat([dtf, new_row_df], ignore_index=True)
            else:
                pass

            # Sort by id
            dtf = dtf.sort_values(by='id').reset_index(drop=True)

            # Save back to CSV
            dtf.to_csv(CSV_File, index=False)
            print("Row added and CSV sorted by id successfully.")

        add_row_to_csv(selected)
        calc_rent_top.destroy()



        rent_date = selected[1]
        rent_time = selected[2]
        return_date = selected[3]
        return_time = selected[4]

        # Convert to datetime
        rent_datetime = datetime.strptime(rent_date + " " + rent_time, "%Y-%m-%d %H:%M:%S")
        return_datetime = datetime.strptime(return_date + " " + return_time, "%Y-%m-%d %H:%M:%S")

        # Calculate difference (absolute to avoid negative hours)
        time_diff = abs(return_datetime - rent_datetime)
        hours_diff = time_diff.total_seconds() / 3600  # total hours as float

        # Calculate total rent
        rate_per_hour = float(selected[15])
        total_rent = round(hours_diff * rate_per_hour, 2)

        messagebox.showinfo(
            "Total Rent",
            f"Total Time : {round(hours_diff, 2)} hours\nRate per hour: {rate_per_hour}\nTotal Amount: {total_rent}"
        )

    calc_rent_top.title("Calculate Rent")

    calc_top_frame = ctk.CTkFrame(calc_rent_top,border_width=2)
    calc_top_frame.pack(padx = 50 ,pady = 50,fill='both',expand = True)

    ctk.CTkLabel(calc_top_frame,text = "Calculate Rent",font=("Arial",22,"bold")).pack(pady = 10)

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[1])
    date_entry_calc.configure(state="disabled")

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[8])
    date_entry_calc.configure(state="disabled")

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[9])
    date_entry_calc.configure(state="disabled")

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[10])
    date_entry_calc.configure(state="disabled")

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[11])
    date_entry_calc.configure(state="disabled")

    date_entry_calc = ctk.CTkEntry(calc_top_frame, width=300, height=40, state="normal")
    date_entry_calc.pack(pady=15)
    date_entry_calc.insert(0, selected[12])
    date_entry_calc.configure(state="disabled")

    ctk.CTkButton(calc_top_frame,text="Calculate",height=40,command = calc_rent_func_final).pack(pady = 15)




def calc_rent():
    for widget in dashboard.winfo_children():
        widget.destroy()
    ctk.CTkLabel(dashboard,text= "Calculate Rent",font=('Arial', 22, 'bold')).pack(padx = 5, pady = 10)

    search(dashboard,RENTED_CSV)
    ctk.CTkButton(filter_frame, text="Calculate Rent", command=calc_rent_func, height=30).pack(side=LEFT, padx=5)







def rent_a_bike_func():
    global date_entry,customer_name_entry,customer_aadhar_no,customer_phone_no,customer_village_no

    top_rent = ctk.CTkToplevel(root)
    top_rent.title("Rent Bike")
    top_rent.geometry("550x650+300+50")

    now = datetime.now()


    for widget in top_rent.winfo_children():
        widget.destroy()

    rent_bike_frame = ctk.CTkFrame(top_rent,border_width=2)
    rent_bike_frame.pack(padx = 50,pady = 50,fill='both',expand = True)

    def rent_final():
        selected = tree.item(tree.focus(), 'values')
        if not selected:
            messagebox.showerror("Error", "Please select a bike first!")
            return

        # ------- Remove from bikes.csv -------

        selected_id = tree.item(tree.focus(), 'values')[0]


        inv_df = pd.read_csv(CSV_File)
        inv_df = inv_df[inv_df['id'] != int(selected_id)]
        inv_df.to_csv(CSV_File, index=False)

        # ------- Add to rented_vehicle.csv -------
        try:
            rent_df = pd.read_csv(RENTED_CSV)
        except FileNotFoundError:
            rent_df = pd.DataFrame(columns=[
                "id", "date", "return", "name", "model", "engine",
                "gear_type", "model_year", "user_name", "aadhar",
                "phone_number", "address", "status"
            ])

        new_row = {
            "id":selected[0],
            "date": now.date(),
            "time":now.strftime("%H:%M:%S"),
            "return": "NAN",
            "ret_time":"NAN",
            "bike_name": selected[1],
            "model": selected[2],
            "engine": selected[3],
            "gear_type": selected[4],
            "model_year": selected[5],
            "user_name": customer_name_entry.get(),
            "aadhar": customer_aadhar_no.get(),
            "phone_number": customer_phone_no.get(),
            "address": customer_village_no.get(),
            "status": "Rented",
            "rate_per_hour":selected[6]
        }

        rent_df = pd.concat([rent_df, pd.DataFrame([new_row])], ignore_index=True)

        rent_df.to_csv(RENTED_CSV, index=False)

        messagebox.showinfo("Rent Bike Successful", f"{selected[1]} rented successfully !!")
        top_rent.destroy()

        # Reload table after deletion
        search(dashboard, CSV_File)



    ctk.CTkLabel(rent_bike_frame,text="Rent Bike",font= ("Arial",22,'bold')).pack(pady=5)

    date_entry = ctk.CTkEntry(rent_bike_frame,placeholder_text= str(now.date()),width=300,height=40)
    date_entry.pack(pady = 15)

    customer_name_entry = ctk.CTkEntry(rent_bike_frame,placeholder_text= "Name",width=300,height=40)
    customer_name_entry.pack(pady = 15)

    customer_aadhar_no = ctk.CTkEntry(rent_bike_frame,placeholder_text= "Aadhar No",width=300,height=40)
    customer_aadhar_no.pack(pady = 15)

    customer_phone_no = ctk.CTkEntry(rent_bike_frame,placeholder_text= "Phone No",width=300,height=40)
    customer_phone_no.pack(pady = 15)

    customer_village_no = ctk.CTkEntry(rent_bike_frame,placeholder_text= "Village",width=300,height=40)
    customer_village_no.pack(pady = 15)

    ctk.CTkButton(rent_bike_frame,text="Rent Bike",height=40,command=rent_final).pack(pady = 15)



def ThemeManager(selected_theme):
    selected_theme = theme_seg.get()
    if selected_theme == 'Light':
        ctk.set_appearance_mode('light')
    elif selected_theme == 'Dark':
        ctk.set_appearance_mode('dark')
    else:
        ctk.set_appearance_mode('system')




def rent_a_bike():
    for widget in dashboard.winfo_children():
        widget.destroy()
    ctk.CTkLabel(dashboard,text= "Rent a Bike Page Coming Soon...",font=('Arial', 22, 'bold')).pack(padx = 5, pady = 10)

    search(dashboard,CSV_File)
    ctk.CTkButton(filter_frame, text="Rent Bike", command=rent_a_bike_func,height=30).pack(side=LEFT, padx=5)



def update_data():
    def update_csv_data():
        data = pd.read_csv(CSV_File)

        # Find the row with the selected ID
        selected_id = selected[0]  # Assuming selected[0] is the ID
        data.loc[data['id'] == float(selected_id), ['name', 'model', 'engine', 'gear_type', 'model_year', 'rate_per_hour']] = [
            update_name.get(),
            update_model.get(),
            update_engine.get(),
            update_gear_type.get(),
            update_model_year.get(),
            update_rate_per_hr.get()
        ]

        # Save the updated CSV
        data.to_csv(CSV_File, index=False)
        messagebox.showinfo("Success", "Data updated successfully!")
        update_top.destroy()
        search(dashboard, CSV_File)

    update_top = ctk.CTkToplevel(root)
    update_top.geometry("650x650+120+120")

    selected = tree.item(tree.focus(), 'values')

    update_top_frame = ctk.CTkFrame(update_top, border_width=2)
    update_top_frame.pack(padx=20, pady=20, expand=True, fill='both')

    update_name = ctk.StringVar(value=selected[1])
    update_model = ctk.StringVar(value=selected[2])
    update_engine = ctk.StringVar(value=selected[3])
    update_gear_type = ctk.StringVar(value=selected[4])
    update_model_year = ctk.IntVar(value=int(selected[5]))
    update_rate_per_hr = ctk.IntVar(value=int(selected[6]))

    ctk.CTkLabel(update_top_frame, text="Update Data", font=('Arial', 24, 'bold')).pack(pady=20)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_name, width=300).pack(pady=10)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_model, width=300).pack(pady=10)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_engine, width=300).pack(pady=10)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_gear_type, width=300).pack(pady=10)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_model_year, width=300).pack(pady=10)
    ctk.CTkEntry(update_top_frame, height=40, textvariable=update_rate_per_hr, width=300).pack(pady=10)

    ctk.CTkButton(update_top_frame, text="Update", command=update_csv_data).pack(ipadx=5, ipady=5, pady=20)




def view_inventory():
    for widget in dashboard.winfo_children():
        widget.destroy()
    ctk.CTkLabel(dashboard, text="Inventory Page",font=('Arial', 22, 'bold')).pack(padx = 5, pady = 10)
    search(dashboard,CSV_File)

    ctk.CTkButton(filter_frame,text='Update Data',command=update_data).pack(side = "right",padx=5,pady=10)


def user():
    global dashboard, sideBar, theme_seg,user_index
    login_frame.pack_forget()

    sideBar = ctk.CTkFrame(root, width=200, border_width=1)
    sideBar.pack(side="left", fill='y', pady=5)

    dashboard = ctk.CTkFrame(root, border_width=1)
    dashboard.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    def logout():
        sideBar.pack_forget()
        dashboard.pack_forget()
        ctk.set_appearance_mode('system')
        main()


    ctk.CTkButton(sideBar, text="Rent Bike", command=rent_a_bike).pack(padx=10, pady=10, ipadx=5, ipady=5)
    ctk.CTkButton(sideBar, text="Calculate Rent", command=calc_rent).pack(padx=10, pady=10, ipadx=5, ipady=5)
    ctk.CTkButton(sideBar, text="View Inventory", command=view_inventory).pack(padx=10, pady=10, ipadx=5, ipady=5)


    logout_frame = ctk.CTkFrame(sideBar, corner_radius=8)
    logout_frame.pack(side='bottom', padx=10, pady=10)

    theme_seg = ctk.CTkSegmentedButton(sideBar, values=["Light", "System", "Dark"], command=ThemeManager)
    theme_seg.set('System')
    theme_seg.pack(pady=10, side='bottom')

    ctk.CTkLabel(logout_frame, text="User Login Logout", height=45).pack()

    ctk.CTkButton(logout_frame, text="Logout", command=logout, fg_color="red", hover_color="darkred").pack(
        padx=5, pady=5, ipadx=5, ipady=7
    )
    with open('data.json','r') as ui:
        data = json.load(ui)


    ctk.CTkLabel(dashboard, text=f"Welcome {data['user'][user_index]['name']}!", font=('Arial', 22, 'bold')).pack(pady=20)



##### Admin Login #####
def admin():
    global dashboard,sideBar,theme_seg
    login_frame.pack_forget()

    sideBar = ctk.CTkFrame(root,width=200,border_width= 1)
    sideBar.pack(side = "left", fill = 'y',pady = 5)

    dashboard = ctk.CTkFrame(root,border_width=1)
    dashboard.pack(side = 'right',fill = 'both' , expand = True,padx = 5,pady = 5)


    def logout():
        sideBar.pack_forget()
        dashboard.pack_forget()
        ctk.set_appearance_mode('system')
        main()

    ctk.CTkButton(sideBar,text = "Home",command = Home).pack(padx = 10, pady = 10,ipadx = 5, ipady = 5)
    ctk.CTkButton(sideBar,text = "Rent Bike",command = rent_a_bike).pack(padx = 10, pady = 10,ipadx = 5, ipady = 5)
    ctk.CTkButton(sideBar,text = "Add New Bike",command = add_new_bike).pack(padx = 10, pady = 10,ipadx = 5, ipady = 5)
    ctk.CTkButton(sideBar,text = "Calculate Rent",command = calc_rent).pack(padx = 10, pady = 10,ipadx = 5, ipady = 5)
    ctk.CTkButton(sideBar,text = "View Inventory",command = view_inventory).pack(padx = 10, pady = 10,ipadx = 5, ipady = 5)



    logout_frame = ctk.CTkFrame(sideBar, corner_radius=8)
    logout_frame.pack(side='bottom', padx=10, pady=10)

    theme_seg = ctk.CTkSegmentedButton(sideBar, values=["Light", "System", "Dark"], command=ThemeManager)
    theme_seg.set('System')
    theme_seg.pack(pady=10, side='bottom')

    ctk.CTkLabel(logout_frame, text="Admin Login Logout", height=45).pack()

    # Logout Button
    ctk.CTkButton(logout_frame, text="Logout", command=logout, fg_color="red",hover_color="darkred").pack(padx=5, pady=5, ipadx=5, ipady=7)
    Home()

if __name__ == '__main__':
    main()