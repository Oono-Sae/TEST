#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧮 簡単な演算計算プログラム
基本的な数学演算を行うプログラム
"""

import math
import statistics

def basic_operations():
    """基本的な四則演算"""
    print("=" * 50)
    print("1. 基本的な四則演算")
    print("=" * 50)
    
    a = 10
    b = 3
    
    print(f"a = {a}, b = {b}")
    print(f"足し算: {a} + {b} = {a + b}")
    print(f"引き算: {a} - {b} = {a - b}")
    print(f"掛け算: {a} × {b} = {a * b}")
    print(f"割り算: {a} ÷ {b} = {a / b:.2f}")
    print(f"余り: {a} ÷ {b} の余り = {a % b}")
    print(f"べき乗: {a} の {b} 乗 = {a ** b}")
    print()

def math_functions():
    """数学関数の使用"""
    print("=" * 50)
    print("2. 数学関数の使用")
    print("=" * 50)
    
    x = 16
    y = 2.5
    angle = 45
    
    print(f"x = {x}, y = {y}, angle = {angle}°")
    print(f"平方根: √{x} = {math.sqrt(x)}")
    print(f"絶対値: |{y}| = {abs(y)}")
    print(f"切り上げ: ⌈{y}⌉ = {math.ceil(y)}")
    print(f"切り捨て: ⌊{y}⌋ = {math.floor(y)}")
    print(f"四捨五入: {y} → {round(y)}")
    print(f"サイン: sin({angle}°) = {math.sin(math.radians(angle)):.4f}")
    print(f"コサイン: cos({angle}°) = {math.cos(math.radians(angle)):.4f}")
    print(f"タンジェント: tan({angle}°) = {math.tan(math.radians(angle)):.4f}")
    print()

def statistics_calculation():
    """統計計算"""
    print("=" * 50)
    print("3. 統計計算")
    print("=" * 50)
    
    numbers = [12, 15, 18, 22, 25, 28, 30, 35, 40, 45]
    
    print(f"数値リスト: {numbers}")
    print(f"合計: {sum(numbers)}")
    print(f"平均: {statistics.mean(numbers):.2f}")
    print(f"中央値: {statistics.median(numbers)}")
    print(f"最小値: {min(numbers)}")
    print(f"最大値: {max(numbers)}")
    print(f"標準偏差: {statistics.stdev(numbers):.2f}")
    print(f"分散: {statistics.variance(numbers):.2f}")
    print()

def sample_calculations():
    """サンプル計算"""
    print("=" * 50)
    print("4. サンプル計算")
    print("=" * 50)
    
    expressions = [
        "2 + 3 * 4",
        "(10 + 5) / 3",
        "2 ** 8",
        "100 % 7",
        "abs(-15)",
        "math.sqrt(144)",
        "math.sin(math.pi/6)"
    ]
    
    for expr in expressions:
        try:
            result = eval(expr)
            print(f"{expr} = {result}")
        except:
            print(f"{expr} = エラー")
    print()

def interactive_calculator():
    """対話的な計算機"""
    print("=" * 50)
    print("5. 対話的な計算機")
    print("=" * 50)
    
    print("🧮 簡単な計算機")
    print("利用可能な演算: +, -, *, /, **, %")
    print("例: 10 + 5, 20 * 3, 100 / 4")
    print("終了するには 'quit' と入力してください")
    
    while True:
        try:
            # ユーザーからの入力
            user_input = input("\n計算式を入力してください: ")
            
            if user_input.lower() == 'quit':
                print("計算機を終了します。")
                break
            
            # 計算の実行
            result = eval(user_input)
            print(f"結果: {result}")
            
        except ValueError:
            print("無効な入力です。数式を入力してください。")
        except ZeroDivisionError:
            print("エラー: 0で割ることはできません。")
        except Exception as e:
            print(f"エラー: {e}")

def practice_problems():
    """練習問題"""
    print("=" * 50)
    print("6. 練習問題")
    print("=" * 50)
    
    print("📝 練習問題")
    print("以下の計算を実行してみてください:")
    print("1. 15 × 7 + 23")
    print("2. (100 - 25) ÷ 5")
    print("3. 2の10乗")
    print("4. 144の平方根")
    print("5. 30度のサイン値")
    
    # 答え
    print("\n答え:")
    print(f"1. 15 × 7 + 23 = {15 * 7 + 23}")
    print(f"2. (100 - 25) ÷ 5 = {(100 - 25) / 5}")
    print(f"3. 2の10乗 = {2 ** 10}")
    print(f"4. 144の平方根 = {math.sqrt(144)}")
    print(f"5. 30度のサイン値 = {math.sin(math.radians(30)):.4f}")
    print()

def main():
    """メイン関数"""
    print("🧮 簡単な演算計算プログラム")
    print("Pythonで基本的な数学演算を実行します")
    print()
    
    # 各機能を実行
    basic_operations()
    math_functions()
    statistics_calculation()
    sample_calculations()
    practice_problems()
    
    # 対話的計算機を実行するかどうか
    print("対話的計算機を起動しますか？ (y/n): ", end="")
    choice = input().lower()
    
    if choice in ['y', 'yes', 'はい']:
        interactive_calculator()
    
    print("\nプログラムを終了します。お疲れさまでした！")

if __name__ == "__main__":
    main()

