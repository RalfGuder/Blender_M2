import csv
import sqlite3
import os

from dbcpy.dbc_file import DBCFile
import dbcpy.records
import configparser
import mathutils



dbc_sql = {"<GenericType(i, 4)>": "INTEGER", 
           "<class 'pywowlib.wdbx.types.DBCString'>": "TEXT",
           "<GenericType(f, 4)>": "FLOAT"}


def check_sql(text) -> '':
    text = text.replace('\'', ' ')
    return text

def createTable(con, name) -> None:
    data = DBCFile(name)

    sql = f"CREATE TABLE [{name}] (\n"
    
    for i in range(len(data.field_types)):
        sql += "    "
        _name = str(data.field_names._fields[i])
        _type = str(data.field_types[i])
        _type = dbc_sql[_type]
        if _name == "ID":
            sql += f"[{_name}] {_type} PRIMARY KEY"
        else:
            sql += f"[{_name}] {_type}"
        if i < len(data.field_types)-1:
            sql += ","
        sql += "\n" 
    sql += ")"
    
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    print(sql)
    
    
    
def read_dbc_file(name, conf):
    pathname = conf['DBC_FILES']['PATH']
    with open(f"{pathname}\\{name}.dbc", 'r+b') as f:
        dbc_file = dbcpy.dbc_file.DBCFile.from_file(f, eval(f"dbcpy.records.{name}Rec"))
    
    return dbc_file
        
def insertTable(con, name) -> None:    
    
    data = DBCFile(name)
    with open(f"C:\\Users\\10170328\\git\\wow-data-dbc\\{name}.dbc", 'rb') as f:
        data.read(f)

    
    feldnamen = []
    for i in range(len(data.field_types)):
        _name = str(data.field_names._fields[i])
        feldnamen.append(_name)
    
    for record in data.records:
        sql = f"INSERT INTO [{name}] VALUES ("
        for i in range(len(feldnamen)):
            _type = str(data.field_types[i])
            _type = dbc_sql[_type]
            feld = feldnamen[i]
            if _type == "TEXT":
                sql += "'" + str(eval(f"check_sql(record.{feld})")) + "'"
            else:
                sql += str(eval(f"record.{feld}"))
            if i < len(feldnamen)-1:
                sql += ", "
        sql += ")"

        print(sql)
        cur = con.cursor()
        try:
            cur.execute(sql)
            con.commit()
        except sqlite3.IntegrityError:  
            pass  
    
def find_model_by_name(modelname, config):
    result = None
    def is_equal(obj, other):
        obj = obj.replace('\\', '/')
        obj = obj.split('/')
        obj = obj[len(obj)-1]
        obj = obj.split('.')
        obj = obj[0]
        obj = obj.strip().lower()

        other = other.replace('\\', '/')
        other = other.split('/')
        other = other[len(other)-1]
        other = other.split('.')
        other = other[0]
        other = other.strip().lower()
        return (obj == other)
    
    pathname = conf['DBC_FILES']['PATH']
    name = "CreatureModelData"
    with open(f"{pathname}\\{name}.dbc", 'r+b') as f:
        dbc_file = dbcpy.dbc_file.DBCFile.from_file(f, eval(f"dbcpy.records.{name}Record"))
        for rec in dbc_file.records:
            if is_equal(modelname, rec.ModelPath.value):
                result = rec
                break
            
    return result

        
def main(config):
    modelname = "raptor"      

    basepath = config['MODELS']['PATH']
    if os.name == 'nt':
        basepath = basepath.replace('/', '\\')
    
    record = find_model_by_name(modelname, config)
    
    modelid = record.ID
    modelpath = ''.join([basepath, "/", record.ModelPath.value])
    if os.name == 'nt':
        modelpath = modelpath.replace('/', '\\')

    filename = ''.join([os.path.dirname(modelpath), '\\', modelname, ".m2"])
    

    model = M2File(4, filename)
    model.read()
    model.find_model_dependencies()
    
    arc = DBCFile(name="CreatureDisplayInfo")
    
    filename = "C:\\Users\\10170328\\git\\wow-data-dbc\\CreatureDisplayInfo.dbc"
    
    f = open(filename, 'rb')
    arc.read(f)
    f.close()
    
    
    file = DBCFile("creatureModelData")
    
    fieldnames = []
   

    """
    with open('CreatureDisplayInfo.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')

        writer.writeheader()
        
        for record in arc.records:
            liste = {}
            for key in fieldnames:
                tmp = f"liste.update({key} = record.{key})"
                eval(tmp)
            writer.writerow(liste)
    
    """
    """
    csvfile = open('CreatureModelData.csv', 'r', newline='')
    result = []
    reader = csv.DictReader(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=';')
    for row in reader:
        result.append(row)
    
    csvfile.close()
  
    contains(result, "creature/raptor/raptor.m2")
    """
    
def matrix_test():
    mat1 : mathutils.Matrix
    mat2 : mathutils.Matrix
    
    mat1 = mathutils.Matrix.to_4x4()
    mat1[0][0:4] = 1.4, 0, 0, 0
    mat2 = mathutils.Matrix.to_4x4()
    
    mat3 = mat1 @ mat2
    
    print(mat3)

if __name__ == "__main__":
    '''
    conf = configparser.ConfigParser()
    conf.read("config.ini", "utf-8")
    
    main(conf)
    '''
    matrix_test()
    
    #with sqlite3.connect(db) as con:
        #createTable(con, "ItemDisplayInfo")
        #insertTable(con, "ItemDisplayInfo")