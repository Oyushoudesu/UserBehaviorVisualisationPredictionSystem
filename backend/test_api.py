import pandas as pd
import requests

try:
    print("\n")
    df = pd.read_csv('data/features/user_features_month4.csv')
    print("特征文件存在")
    print(f"用户数：{len(df)}")
    print(f"前5个用户id:{df['user_id'].head().tolist()}")
except Exception as e:
    print(f"加载特征文件失败: {e}")

# 测试健康检查
try:
    print("\n")
    res = requests.get("http://localhost:8000/health")
    print(f"健康检查状态码: {res.status_code}")
    print(f"健康检查响应: {res.json()}")
except Exception as e:
    print(f"健康检查请求失败: {e}")

# 测试总览
try:
    print("\n")
    res = requests.get("http://localhost:8000/api/v1/visualization/overview")
    print(f"总览状态码: {res.status_code}")
    print(f"总览响应: {res.json()}")
    data = res.json()
    print(f"用户数: {data.get('total_users')}")
    print(f"CVR: {data.get('cvr')}")
except Exception as e:
    print(f"总览请求失败: {e}")


# 测试top用户
try:
    print("\n")
    res = requests.get("http://localhost:8000/api/v1/statistics/top-users?top_n=5")
    print(f"Top用户状态码: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"返回数据：")
        print(f" {data}")
    else:
        print(f"error:{res.text}")
except Exception as e:
    print(f"Top用户请求失败: {e}")

# 测试实际存在的用户ID测试预测
try:
    # 从特征文件获取真实用户ID进行测试
    print("\n")
    test_user = df['user_id'].head(3).astype(str).tolist()
    print(f"测试用户ID: {test_user}")
    res = requests.post(
        "http://localhost:8000/api/v1/prediction/repurchase",
        json={
            "user_ids": test_user,
            "model_type": "regular"
        }
    )
    print(f"状态码: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print("预测成功:")
        for pred in data[:2]:
            print(f"    用户{pred['user_id']}概率: {pred['probability']:.4f},预测={pred['prediction']}")
    else:
        print(f"error:{res.text}")
except Exception as e:
    print(f"预测请求失败: {e}")

