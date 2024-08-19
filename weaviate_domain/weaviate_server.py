import weaviate



def create_schema(client):
    ## 该函数禁用 ##
    """
    创建新的 Schema（相当于创建表）的函数。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    schema (dict): 定义 Schema 的字典，包括多个类。

    返回:
    None
    """
    minimal_schema = {
        "classes": [
            {
                "class": "Placeholder",  # 占位符类，可以理解为一个空的类
                "description": "A minimal placeholder class.",
                "properties": []
            }
        ]
    }

    try:
        # 创建新的 Schema
        client.schema.create(minimal_schema)
        print("Schema created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_basic_user_class_schema(user_id):
    """
    根据用户 ID 生成一个没有属性的基础 Weaviate 类的 Schema。
    
    参数:
    user_id (str): 用户 ID，将作为类名使用。
    
    返回:
    dict: 包含基础类结构的字典，没有任何属性。
    """
    return {
        "class": f"User_{user_id}",  # 使用用户 ID 作为类名
        "description": f"An empty entity for user {user_id}.",
        "properties": []  # 没有属性
    }

def add_class_to_existing_schema(client, new_class):
    """
    向现有 Schema 中添加新类（相当于向表中添加新类）的函数。
    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    new_class (dict): 定义新类的字典。
    返回:
    None
    """
    try:
        # 添加新类到现有 Schema
        # 即使是创建的最基础的类也会有很多默认配置，这些配置是 Weaviate 为了优化查询性能、
        # 数据管理和扩展性所必需的，尽管它们在你创建类时可能未被显式指定。
        # Weaviate 自动为每个类添加这些配置，以确保系统能够正常运行，并为将来的扩展做好准备。
        client.schema.create_class(new_class)
        print(f"Class '{new_class['class']}' added successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_classes_starting_with(client, prefix="User_"):
    # 查询以prefix开头的所有的类有哪些

    """
    查询 Schema 中以特定字符串开头的类。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    prefix (str): 用于过滤类名的前缀字符串。

    返回:
    list: 包含所有以特定前缀开头的类名列表。
    """
    try:
        schema = client.schema.get()  # 获取整个 Schema
        classes = schema.get('classes', [])  # 提取类列表
        filtered_classes = [cls['class'] for cls in classes if cls['class'].startswith(prefix)]
        return filtered_classes
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_class_schema(client, class_name):
    """
    获取 Weaviate 中某个类的数据结构（Schema）。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    class_name (str): 要查询的类名。

    返回:
    dict: 包含类的 Schema 信息的字典，如果类不存在则返回 None。
    """
    try:
        schema = client.schema.get()  # 获取整个 Schema
        classes = schema.get('classes', [])
        
        for cls in classes:
            if cls['class'] == class_name:
                return cls  # 返回匹配的类结构
        
        print(f"Class '{class_name}' not found.")
        return None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def add_properties_to_class(client, class_name, new_properties):
    """
    向已有的 Weaviate 类中添加属性（properties）。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    class_name (str): 要更新的类名。
    new_properties (list): 要添加的属性列表，每个属性是一个字典。

    返回:
    None
    """
    try:
        for prop in new_properties:
            client.schema.property.create(class_name, prop)
        print(f"Properties added to class '{class_name}' successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_empty_object(client, class_name):
    """
    在 Weaviate 中创建一个空对象，不为其赋值任何属性。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    class_name (str): 类名。

    返回:
    dict: 创建的对象的响应数据。
    """
    try:
        response = client.data_object.create(
            data_object={},  # 不设置任何属性值
            class_name=class_name
        )
        print(f"Empty object created in class '{class_name}' successfully!")
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def update_object_property(client, class_name, object_id, updated_properties):
    """
    更新 Weaviate 中指定对象的属性值。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    class_name (str): 类名。
    object_id (str): 要更新的对象的 UUID。
    updated_properties (dict): 包含要更新的属性及其值的字典。

    返回:
    dict: 更新后的对象的响应数据。
    """
    try:
        client.data_object.update(
            data_object=updated_properties,
            class_name=class_name,
            uuid=object_id
        )
        print(f"Object in class '{class_name}' updated successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_object_data(client, class_name, object_id):
    """
    获取 Weaviate 中指定对象的所有数据。

    参数:
    client (weaviate.Client): Weaviate 客户端实例。
    class_name (str): 类名。
    object_id (str): 要获取的对象的 UUID。

    返回:
    dict: 对象的所有数据。
    """
    try:
        response = client.data_object.get(
            uuid=object_id,
            class_name=class_name
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def main():
    ## 创建空类
    # new_class = create_basic_user_class_schema('1')
    # add_class_to_existing_schema(client, new_class)

    ## 获取schema中有哪些类（以某字符串开头的类）
    # schema_class = get_classes_starting_with(client)

    ##获取类的结构
    # class_name = "User_1"
    # class_schema = get_class_schema(client, class_name)
    # print(class_schema)

    ## 向类中添加属性
#     new_properties = [
#     {
#         "name": "sex",
#         "dataType": ["text"],
#         "description": "用户的性别."
#     }
# ]
#     add_properties_to_class(client, "User_1", new_properties)

    # # 在 "User_1" 类中创建一个空对象，对象的uuid：4fb8c81b-60dd-4ba9-b7c8-65c3bc498e72
    # class_name = "User_1"
    # response = create_empty_object(client, class_name)
    # print(response)

    # #对对象的属性进行赋值
    # # 如果类中添加了新的属性，然后对象也想用这个属性，也可以用这个操作
    # # 假设你已经有一个对象的 UUID
    # object_id = "4fb8c81b-60dd-4ba9-b7c8-65c3bc498e72"  # 替换为实际的对象 UUID
    # # 要更新的属性值
    # updated_properties = {
    #     "name": "小洪"  # 更新 mingzi 属性的值为 "小洪"
    # }
    # # 更新 "User_1" 类中指定对象的属性值
    # class_name = "User_1"
    # update_object_property(client, class_name, object_id, updated_properties)

    # # 查看对象中所有的数据
    # 假设你已经有一个对象的 UUID
    # 查询对象的数据时，返回的结果中只会显示已经为对象赋值的属性。未赋值的属性不会出现在查询结果中
    object_id = "4fb8c81b-60dd-4ba9-b7c8-65c3bc498e72"  # 替换为实际的对象 UUID
    # 获取 "User_1" 类中指定对象的所有数据
    class_name = "User_1"
    object_data = get_object_data(client, class_name, object_id)
    print(object_data)


if "__main__":
    client = weaviate.Client(
    url="http://localhost:8080",  # Weaviate 的 URL
    auth_client_secret=weaviate.AuthApiKey(api_key="WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih")  # 替换为你的 API 密钥
)
    main()


