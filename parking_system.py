import pymysql as py

class DBHelper:
    def __init__(self):
        self.con = py.connect(  
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'yash_parking_valet',
            port = 3306
        )
        print("Your database connect!!")
        self.cursor = self.con.cursor()
        
    def reset_system(self):
        try: 
             self.cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
             self.cursor.execute('TRUNCATE table vehicle_database')
             self.cursor.execute('TRUNCATE table parking_database')
             self.cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
             self.con.commit()
             print("database fully reset successfully!!!")
        except Exception as e:
            print(f"Error due to: {e}")             

# create database of parking and vehicle   
    def parking_database(self):
        query = "create table if not exists Parking_database(slot_id int auto_increment primary key , slot_name VARCHAR(20), Status VARCHAR(20) default 'Available')"
        self.cursor.execute(query)
        print("Your parking database is created")
    
    def vehicle_database(self):
        query = 'create table if not exists Vehicle_database(log_id int auto_increment primary key, vehicle_number VARCHAR(10) NOT NULL, slot_id int, entry_time DATETIME default current_timestamp , exit_time DATETIME, foreign key(slot_id) references Parking_database(slot_id))'
        self.cursor.execute(query)
        print("Vehicle database created!!")
        
    # generate the slots for parking vehicles     
    def generate_slots(self,total_needed):
        try:
            #checking the available slots
            self.cursor.execute('SELECT COUNT(*) FROM parking_database')
            current_count = self.cursor.fetchone()[0]   #find the value at 1st index
            
            if total_needed>current_count:
                new_slots = total_needed - current_count
                for i in range(1 , new_slots+1):
                    s_id = current_count + i
                    s_name = f"Slot - {s_id}"  
                    query = "INSERT INTO parking_database(slot_name,Status) values(%s , 'AVAILABLE')"
                    self.cursor.execute(query,(s_name,))
                self.con.commit()
                print(f"Successfully added new slots: {new_slots}")
            else: 
                print(f"already have sufficient slots {current_count}")
        except Exception as e:
            print(f"Slots generation error {e}")
    
    #Auto allocation and entry logic
    def park_vehicle_auto(self , vehicle_number):
        try:
            #check if vehicle already exist or not
            self.cursor.execute("SELECT log_id from vehicle_database where vehicle_number = %s AND exit_time is NULL", (vehicle_number))
            already_parked = self.cursor.fetchone()
            if already_parked:
                print(f"Vehicle number {vehicle_number} is already parked!!")
                return
            
            #check available slots then giving slots to vehicle 
            self.cursor.execute("SELECT slot_id, slot_name from parking_database WHERE Status = 'AVAILABLE' LIMIT 1")
            row = self.cursor.fetchone()
            if row:
                s_id,s_name = row 
                #entry of vehicle in premises with automaticlly timestamp .
                self.cursor.execute("INSERT INTO vehicle_database(vehicle_number,slot_id) values (%s,%s)", (vehicle_number,s_id))
                
                #update the parking database 
                self.cursor.execute("Update parking_database SET Status = 'OCCUPIED' where slot_id = '%s'",(s_id))
                
                self.con.commit()
                print("Vehicle Parked!!")
                print(f"Vehicle Number : {vehicle_number}")
                print(f"Parking Slot ID : {s_name}")
            
            else:
                print("\n Parking slots are full!!!")
        except Exception as e:
            print(f"parking slots error {e}")

    # exit vehicle function 
    def exit_vehicle(self , vehicle_number):
        try:
            self.cursor.execute("Select slot_id from vehicle_database WHERE vehicle_number = %s AND exit_time is NULL",(vehicle_number,))
            result = self.cursor.fetchone()
            
            if result:
                slot_id = result[0]
                # exit the time and then free the available label
                self.cursor.execute("UPDATE vehicle_database SET exit_time = NOW() WHERE vehicle_number = %s AND exit_time is NULL " , (vehicle_number,))
                
                # Change the occupied slot to available slot
                self.cursor.execute("UPDATE parking_database SET Status = 'AVAILABLE' where slot_id = %s", (slot_id,))
                
                self.con.commit()
                print(f"Successfully, Vehicle {vehicle_number} has exited. Slot {slot_id} is now Available ")
            
            else:
                print(f"Vehicle {vehicle_number} will not available in parking!!")
        
        except Exception as e:
            print(f"Exit Error will be {e}")
            
    # dashboard services : show vehicle , status and everything 
    def dashboard(self):
        self.cursor.execute("SELECT COUNT(*) FROM parking_database")
        total_parking = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) from parking_database where Status='AVAILABLE'")
        Available_status = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) from parking_database where Status='OCCUPIED'")
        occupied_status = self.cursor.fetchone()[0]
            
        self.cursor.execute("SELECT COUNT(*) from vehicle_database where exit_time is NULL")
        Active_status = self.cursor.fetchone()[0]  
        
        print("\n ----- DASHBOARD -----")
        print(f"Total Slots: {total_parking}")
        print(f"Available Slots: {Available_status}")
        print(f"Occupied Status: {occupied_status}")
        print(f"Currently Parked Vehicle: {Active_status}")  
        
      
#main coding
helper = DBHelper()
helper.parking_database()
helper.vehicle_database()

#generate slots:
helper.generate_slots(12)
# 
#insert the user vehicle number
user_vehicle_number = input("Enter the Vehicle Number: ")
helper.park_vehicle_auto(user_vehicle_number)


exit_vehicle_number = input("Enter the Vehicle number you want to exit: ")
helper.exit_vehicle(exit_vehicle_number)



#helper.reset_system()
helper.dashboard()