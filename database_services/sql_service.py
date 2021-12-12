import sqlite3
import os

file_path = os.path.realpath(__file__)
app_dir = os.path.dirname(os.path.dirname(file_path))
db_path = os.path.join(app_dir, 'db', 'LYPZ.db')

DATABASE = db_path


class SqliteService:

    @classmethod
    def get_db(cls):
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
        except Exception as e:
            print(e)

        return conn

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):
        connection = cls.get_db()
        try:
            cur = connection.execute(sql_statement, args)
            connection.commit()
            if fetch:
                res = cur.fetchall()
                return res

        except Exception as e:
            connection.close()
            raise e
        finally:
            connection.close()

    @classmethod
    def get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = []
        else:
            for k, v in template.items():
                terms.append(k + "=?")
                args.append(v)

            clause = " WHERE " + " AND ".join(terms)

        return clause, args

    @classmethod
    def select(cls, table_name, template={}):
        wc, args = cls.get_where_clause_args(template)

        query = "SELECT * FROM " + table_name + " " + wc

        return cls.run_sql(query, args, True)

    @classmethod
    def insert(cls, table_name, insert_data):

        cols = []
        vals = []
        args = []

        for k, v in insert_data.items():
            cols.append(k)
            vals.append('?')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        query = "insert into " + table_name + " " + cols_clause + \
                " " + vals_clause

        print(query)
        print(args)

        res = cls.run_sql(query, args)

        return res

    @classmethod
    def update(cls, table_name, update_data, template):

        wc, wc_args = cls.get_where_clause_args(template)

        cols = []
        args = []

        for k, v in update_data.items():
            cols.append(k + '=?')
            args.append(v)

        cols_clause = ",".join(cols)

        query = "UPDATE " + table_name + " SET " + cols_clause + " " + wc

        args.extend(wc_args)

        res = cls.run_sql(query, args)

        return res

    @classmethod
    def delete(cls, table_name, template):
        wc, args = cls.get_where_clause_args(template)

        query = "DELETE FROM " + table_name + " " + wc

        res = cls.run_sql(query, args)

        return res

    @classmethod
    def find_in_condition(
        cls, table_name, select_vars, in_variable, in_values
    ):

        select_clause = "*"
        if select_vars is not None:
            select_clause = ",".join(select_vars)
        for i in range(len(in_values)):
            in_values[i] = '"' + in_values[i] + '"'

        in_values_clause = ",".join(in_values)
        query = "SELECT " + select_clause + " FROM " + \
            table_name + " WHERE " + \
            in_variable + " in (" + in_values_clause + ")"

        res = cls.run_sql(query)

        return res
