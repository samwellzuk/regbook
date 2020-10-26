from data.dbmgr import DBManager

if __name__ == '__main__':
    try:
        dbmgr = DBManager()
        dbmgr.auth('zy', '456', 'LocalHost')
        print(dbmgr.get_user_name())
        print(dbmgr.is_admin())
        # if dbmgr.auth('zy', '456', 'LocalHost'):
        #     dbmgr.change_pwd('123', '456')
    except Exception as e:
        print(str(e))
