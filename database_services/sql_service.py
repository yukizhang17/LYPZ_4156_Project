# import pymysql
# import json
# import logging
# from flask import g
import sqlite3
import os

file_path = os.path.realpath(__file__)
file_path = "/".join(file_path.split("/")[0: -2])

DATABASE = file_path + '/db/LYPZ.db'


class SqliteService:

    @classmethod
    def get_db(self):
        conn = None
        try:
            conn = sqlite3.connect(DATABASE)
        except Exception as e:
            print(e)

        return conn

    @classmethod
    def run_sql(self, sql_statement, args, fetch=False):
        connection = self.get_db()
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
    def get_where_clause_args(self, template):

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
    def select(self, table_name, template={}):
        wc, args = self.get_where_clause_args(template)

        query = "SELECT * FROM " + table_name + " " + wc

        return self.run_sql(query, args, True)

    @classmethod
    def insert(self, table_name, insert_data):

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

        res = self.run_sql(query, args)

        return res

    @classmethod
    def update(self, table_name, update_data, template):

        wc, wc_args = self.get_where_clause_args(template)

        cols = []
        # vals = []
        args = []

        for k, v in update_data.items():
            cols.append(k + '=?')
            # vals.append('%s')
            args.append(v)

        cols_clause = ",".join(cols)

        query = "UPDATE " + table_name + " SET " + cols_clause + " " + wc

        args.extend(wc_args)

        res = self.run_sql(query, args)

        return res

    @classmethod
    def delete(self, table_name, template):
        wc, args = self.get_where_clause_args(template)

        query = "DELETE FROM " + table_name + " " + wc

        res = self.run_sql(query, args)

        return res

    @classmethod
    def find_in_condition(self, table_name, select_vars, in_variable, in_values):

        select_clause = "*"
        if select_vars is not None:
            select_clause = ",".join(select_vars)
        for i in range(len(in_values)):
            in_values[i] = '"' + in_values[i] + '"'

        in_values_clause = ",".join(in_values)
        query = "SELECT " + select_clause + " FROM " + \
            db_schema + "." + table_name + " WHERE " + \
            in_variable + " in (" + in_values_clause + ")"

        res = self.run_sql(query)

        return res
