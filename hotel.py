import tkinter as tk
from tkinter import ttk
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
import io
import random
# root = tk.Tk()
# app = HotelManagementSystem(root)
class HotelManagement:
    def __init__(self, root):
        self.menu_items = {
            "Burger   ": 200,
            "Pizza    ": 300,
            "Pasta    ": 250,
            "Salad    ": 100,
            "Steak    ": 150,
            "Chips    ": 50,
            "Sandwich ": 100,
            "Tea      ": 50,
            "Coffee   ": 80,
            "Dessert  ": 200
        }
        self.menu_var = tk.StringVar()
        try:
            self.conn = sqlite3.connect("hotel_database.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                                CREATE TABLE IF NOT EXISTS orders (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    date TEXT,
                                    table_number TEXT,
                                    payment_method TEXT,
                                    total_price REAL
                                )
                            ''')
            self.conn.commit()

            

            self.cursor.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1")
            last_id = self.cursor.fetchone()
            if last_id:
                self.customer_id = last_id[0] + 1
            else:
                self.customer_id = random.randint(1000, 9999)


            # Creating a window
            self.root = root
            self.root.title("Hotel Management System")
            self.root.geometry("1200x800")
            self.root.configure(bg="#e6e6e6")
            self.pay_opt=["Phone-pay","Google-pay","Cash","Card"]
            self.selected_items = []

            # Left Frame
            self.left_frame = tk.Frame(root, bg="#d9d9d9", padx=20, pady=20)
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Menu Frame
            self.menu_frame = tk.Frame(self.left_frame, bg="#d9d9d9")
            self.menu_frame.pack(pady=(0, 40))

            self.menu_label = tk.Label(self.menu_frame, text="Menu:", font=("Helvetica", 12,"bold"), bg="#d9d9d9")
            self.menu_label.grid(row=0, column=0, padx=(0, 10))
            self.menu_dropdown = ttk.Combobox(self.menu_frame, values=list(self.menu_items.keys()))
            self.menu_dropdown.grid(row=0, column=1, padx=(0, 10))

            # Cost Label and Entry
            
            self.cost_var = tk.StringVar()  # Variable to hold the cost
            
            self.menu_var.trace('w', self.update_cost)
            # Quantity input
            self.quantity_label = tk.Label(self.menu_frame, text="Quantity:", font=("Helvetica", 12,"bold"), bg="#d9d9d9")
            self.quantity_label.grid(row=2, column=0, padx=(0,10), pady=10)
            # self.quantity_entry = tk.Entry(self.menu_frame)
            # self.quantity_entry.grid(row=2, column=1, padx=(0, 10))
            # self.quantity_entry.insert(0,'1')
            self.quantity_decrease_btn = tk.Button(
                self.menu_frame,
                text="-",
                command=self.decrease_quantity,
                font=("Helvetica", 10,"bold"),
                bg="white",
                fg="black",
                width=1
            )
            self.quantity_decrease_btn.grid(row=2, column=0, padx=(90,0))

            self.quantity_entry = tk.Entry(self.menu_frame)
            self.quantity_entry.grid(row=2, column=1)
            self.quantity_entry.insert(0,'1')

            self.quantity_increase_btn = tk.Button(
                self.menu_frame,
                text="+",
                command=self.increase_quantity,
                font=("Helvetica", 10,"bold"),
                bg="white",
                fg="black",
                width=1
            )
            self.quantity_increase_btn.grid(row=2, column=3)

            #payment options
            self.pay_frame = tk.Frame(self.left_frame, bg="#d9d9d9")
            self.pay_frame.pack(pady=(0, 10))
            self.pay_label = tk.Label(self.pay_frame, text="payment:", font=("Helvetica", 12,"bold"), bg="#d9d9d9")
            self.pay_label.grid(row=0, column=0, padx=(0, 10))
            self.pay_var = tk.StringVar()
            self.pay_dropdown = ttk.Combobox(self.pay_frame, textvariable=self.pay_var, values=self.pay_opt)
            self.pay_dropdown.grid(row=0, column=1, padx=(0, 10))

            # Update Graph Button
            self.update_graph_button = tk.Button(
                self.left_frame,
                text="Graph",
                command=self.update_graph,
                font=("Helvetica", 12),
                bg="pink",
                fg="white",
                width=15,
                height=1
            )
            self.update_graph_button.pack(pady=(10, 0))

            # Graph Frame
            self.graph_frame = tk.Frame(self.left_frame, bg="#d9d9d9")
            self.graph_frame.pack(pady=(20, 0))
            self.graph_label = tk.Label(self.graph_frame, text="Graph:", font=("Helvetica", 12,"bold"), bg="#d9d9d9")
            self.graph_label.grid(row=0, column=0)
            self.menu_quantities = {item: 0 for item in self.menu_items}
            self.pie_chart = None
            self.graph_canvas = tk.Canvas(self.graph_frame, bg="#d9d9d9", width=500, height=500)
            self.graph_canvas.grid(row=1, column=0, pady=(10, 0))

            # Right Frame
            self.right_frame = tk.Frame(root, bg="#e6e6e6", padx=20, pady=20)
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Date and Customer Info Frame
            self.date_frame = tk.Frame(self.right_frame, bg="#e6e6e6")
            self.date_frame.pack(pady=(0, 10))
            self.date_label = tk.Label(self.date_frame, text="Date and Time:", font=("Helvetica", 12,"bold"), bg="#e6e6e6")
            self.date_label.grid(row=0, column=0, padx=(0, 243))
            self.date_var = tk.StringVar()
            self.date_label_value = tk.Label(self.date_frame, textvariable=self.date_var, font=("Helvetica", 12), bg="#e6e6e6")
            self.date_label_value.grid(row=0, column=2, padx=(0, 365))
            self.update_date()

            self.customer_id_label = tk.Label(self.date_frame, text=f"Customer ID: {self.customer_id}", font=("Helvetica", 12,"bold"), bg="#e6e6e6")
            self.customer_id_label.grid(row=3, column=0, padx=(0, 250))
            self.table_number_label = tk.Label(self.date_frame, text="Table Number:", font=("Helvetica", 12,"bold"), bg="#e6e6e6")
            self.table_number_label.grid(row=4, column=0, padx=(0, 250))
            self.table_number_entry = tk.Entry(self.date_frame, width=100)
            self.table_number_entry.grid(row=4, column=2, padx=(0,100))
            
            # Table Frame
            self.table_frame = tk.Frame(self.right_frame, bg="black")
            self.table_frame.pack(pady=50)

            # Increase height and width of the table
            table_height = 25
            table_width = 30
            self.table = ttk.Treeview(self.table_frame, columns=("QUANTITY", "ITEM", "COST"), show="headings",height=table_height)

            # Set headings
            self.table.heading("#1", text="QUANTITY", anchor=tk.W)
            self.table.heading("#2", text="ITEM", anchor=tk.W)
            self.table.heading("#3", text="COST", anchor=tk.W)

            # Set column widths
            column_widths = [210, 210, 210]
            for i, width in enumerate(column_widths):
                self.table.column("#{}".format(i), width=width, anchor=tk.W)

            self.table.pack(fill=tk.BOTH, expand=True)

            # Buttons Frame
            buttons_frame = tk.Frame(self.right_frame, bg="#d9d9d9", width=sum(column_widths))
            buttons_frame.pack(pady=(2, 3))

            # Total Button
            self.total_button = tk.Button(
                buttons_frame,
                text="Total",
                command=self.calculate_total,
                font=("Helvetica", 12),
                bg="pink",
                fg="white",
                width=15,
                height=1
            )
            self.total_button.pack(side=tk.LEFT, padx=(0, 10))

            # Update Table Button
            self.update_button = tk.Button(
                buttons_frame,
                text="Update Table",
                command=self.update_table,
                font=("Helvetica", 12),
                bg="pink",
                fg="white",
                width=15,
                height=1
            )
            self.update_button.pack(side=tk.LEFT, padx=(0, 10))

            # self.update_database_button = tk.Button(
            #     buttons_frame,
            #     text="Update Database",
            #     command=self.update_database,
            #     font=("Helvetica", 12),
            #     bg="blue",
            #     fg="white",
            #     width=15,
            #     height=1
            # )
            # self.update_database_button.pack(side=tk.LEFT, padx=(0, 10))

            # self.history_button = tk.Button(
            #     buttons_frame,
            #     text="History",
            #     command=self.show_history,
            #     font=("Helvetica", 12),
            #     bg="#2196f3",
            #     fg="white",
            #     width=15,
            #     height=1
            # )
            # self.history_button.pack(side=tk.LEFT, padx=(0, 10))
            # Reset Button
            self.reset_button = tk.Button(
                buttons_frame,
                text="Reset",
                command=self.reset_entries,
                font=("Helvetica", 12),
                bg="pink",
                fg="white",
                width=15,
                height=1
            )
            self.reset_button.pack(side=tk.LEFT, padx=(0, 10))

        except Exception as e:
            print(f"An error occurred : {e}")


    def update_date(self):
        try:
            now = datetime.now()
            formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
            self.date_var.set(formatted_date)
            self.root.after(1000, self.update_date)
        except Exception as e:
            print(f"An error occurred in update_date: {e}")

    def calculate_total(self):
        try:
            total_cost = 0
            for child in self.table.get_children():
                cost_value = self.table.item(child, 'values')[2]
                total_cost += float(cost_value)
            for child in self.table.get_children():
                if self.table.item(child, 'values')[1] == "Total":
                    self.table.delete(child)
            self.table.insert("", "end", values=("Total", "", total_cost))
            self.total_button.pack(pady=(10, 0))

        except Exception as e:
            print(f"An error occurred in calculate_total: {e}")

    def increase_quantity(self):
        current_quantity = self.quantity_entry.get()
        if current_quantity.isdigit():
            new_quantity = int(current_quantity) + 1
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(new_quantity))

    def decrease_quantity(self):
        current_quantity = self.quantity_entry.get()
        if current_quantity.isdigit():
            new_quantity = int(current_quantity) - 1 if int(current_quantity) > 0 else 0
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(new_quantity))

    def update_table(self):
        try:
            item = self.menu_dropdown.get()
            quantity = float(self.quantity_entry.get())
            
            if item in self.menu_items:
                cost = self.menu_items[item]
                total_cost = cost * quantity

                if item in self.menu_quantities:
                    self.menu_quantities[item] += quantity

                self.table.insert("", "end", values=(quantity, item, total_cost))
        except Exception as e:
            print(f"An error occurred in update_table: {e}")

    def update_cost(self, *args):
        selected_item = self.menu_var.get()
        if selected_item in self.menu_items:
            item_cost = self.menu_items[selected_item]
            self.cost_var.set(f"${item_cost:.2f}")  # Display the cost in the entry
        else:
            self.cost_var.set("")  # If item not found, clear the cost entry
    
    def get_total(self):
        try:
            total_cost = 0
            children = self.table.get_children()
            for child in children[:-1]:
                cost_value = self.table.item(child, 'values')[2]
                total_cost += float(cost_value)

            return total_cost
        except Exception as e:
            print(f"An error occurred in get_total: {e}")
        
    def reset_quantities(self):
        self.menu_quantities = {item: 0 for item in self.menu_items}


    def reset_entries(self):
        try:
            # Clear other entries and the table
            for child in self.table.get_children():
                self.table.delete(child)

            self.menu_dropdown.set("")
            self.quantity_entry.delete(0, tk.END)
            # Clear the cost entry
            self.cost_var.set("")  # Assuming cost_var is the associated variable for cost entry
            self.table_number_entry.delete(0, tk.END)
            self.reset_payment_and_chart()
            self.reset_quantities()

        except Exception as e:
            print(f"An error occurred in reset_entries: {e}")

    def update_database(self):
        try:
            total_price = self.get_total() if self.table.get_children() else 0.0
            date = self.date_var.get()
            table_number = self.table_number_entry.get()
            payment_method = self.payment_method_entry.get()

            # Insert the data into the database
            self.cursor.execute('''
                        INSERT INTO orders (date, table_number, payment_method, total_price)
                        VALUES (?, ?, ?, ?)
                    ''', (date, table_number, payment_method, total_price))
            self.conn.commit()

            # Increment the customer ID for the next entry
            self.customer_id += 1
            self.customer_id_label.config(text=f"Customer ID: {self.customer_id}")

            print("Data added to the database.")
        except Exception as e:
            print(f"An error occurred in update_database: {e}")

    def _del_(self):
        try:
            self.conn.close()
        except Exception as e:
            print(f"An error occurred in _del_: {e}")

    def show_history(self):
        try:
            history_window = tk.Toplevel(self.root)
            history_window.title("Order History")
            history_window.geometry("600x400")
            history_table = ttk.Treeview(history_window,columns=("ID", "Date", "Table Number", "Payment Method", "Total Price"),show="headings", height=15)
            history_table.heading("#1", text="ID", anchor=tk.W)
            history_table.heading("#2", text="Date", anchor=tk.W)
            history_table.heading("#3", text="Table Number", anchor=tk.W)
            history_table.heading("#4", text="Payment Method", anchor=tk.W)
            history_table.heading("#5", text="Total Price", anchor=tk.W)
            self.cursor.execute("SELECT * FROM orders")
            rows = self.cursor.fetchall()
            for row in rows:
                history_table.insert("", "end", values=row)

            history_table.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"An error occurred in show_history: {e}")

    def update_graph(self):
        try:
            # Gather data for the pie chart
            labels = []
            values = []

            for item, quantity in self.menu_quantities.items():
                if quantity > 0:
                    labels.append(item)
                    values.append(quantity)

            # Close previous pie chart, if any
            if self.pie_chart:
                plt.close(self.pie_chart)

            # Plot the pie chart only for items with a non-zero quantity
            if labels:
                self.pie_chart = plt.figure(figsize=(5, 5))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title('Menu Item Distribution')

                # Convert the pie chart to a Tkinter PhotoImage
                pie_image = self.plot_to_image()

                # Update the graph canvas with the new image
                self.graph_canvas.create_image(0, 0, anchor=tk.NW, image=pie_image)
                self.graph_canvas.image = pie_image  # Keep a reference to avoid garbage collection

        except Exception as e:
            print(f"An error occurred in update_graph: {e}")

    def reset_payment_and_chart(self):
        try:
            # Reset the payment option
            self.pay_dropdown.set("")  # Reset the payment dropdown to its default value

            # Reset the pie chart
            if self.pie_chart:
                plt.close(self.pie_chart)  # Close the previous pie chart
                self.graph_canvas.delete("all")  # Clear the graph canvas

            # Reset other relevant fields as needed
            # For instance, if there are specific variables to reset or entries to clear, you can do so here.

        except Exception as e:
            print(f"An error occurred in reset_payment_and_chart: {e}")

    def plot_to_image(self):
        """Convert the current matplotlib plot to a Tkinter PhotoImage."""
        plt.close(self.pie_chart)
        buf = io.BytesIO()
        self.pie_chart.savefig(buf, format='png')
        buf.seek(0)
        return tk.PhotoImage(data=buf.read())

root = tk.Tk()
app = HotelManagement(root)
root.mainloop()

