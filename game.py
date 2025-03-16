import random

# ===== 游戏核心数据 =====
game_state = {
    'player_hp': 5,
    'enemy_hp': 5,
    'chamber': [],
    'current_pos': 0,
    'knife_charged': False,
    'smoke_active': 0,
    'inventory': {
        '放大镜': 0,
        '刀': 0,
        '啤酒': 0,
        '饮料': 0,
        '烟': 0,
        '肾上腺素': 0,
        '药': 0,
        '手机': 0,
        '逆转器': 0
    }
}

def init_chamber():
    """初始化枪膛并智能补充道具"""
    total = random.randint(3, 9)
    live = random.randint(1, total-1)
    game_state['chamber'] = ['实弹']*live + ['空包弹']*(total-live)
    random.shuffle(game_state['chamber'])
    
    # 智能补给系统
    current_total = sum(game_state['inventory'].values())
    max_add = 12 - current_total
    
    if max_add > 0:
        print("\n=== 补给 ===")
        items = list(game_state['inventory'].keys())
        random.shuffle(items)
        
        remaining = max_add
        additions = {item:0 for item in items}
        
        # 基础分配
        for item in items:
            if remaining <= 0: break
            add = min(1, remaining)
            additions[item] += add
            remaining -= add
        
        # 随机分配剩余
        while remaining > 0:
            item = random.choice(items)
            max_possible = min(3 - additions[item], remaining)
            if max_possible > 0:
                add = random.randint(0, max_possible)
                additions[item] += add
                remaining -= add
        
        # 应用补给
        for item, add in additions.items():
            game_state['inventory'][item] += add
            if add > 0:
                print(f"· {item}+{add}")
        print(f"总数：{sum(game_state['inventory'].values())}/12")
        print("============")
    
    game_state['current_pos'] = 0
def show_status():
    """显示游戏状态"""
    remain = len(game_state['chamber']) - game_state['current_pos']
    print(f"\n玩家HP：{game_state['player_hp']}  敌人HP：{game_state['enemy_hp']}")
    print(f"剩余子弹：{remain}发")
    print("道具清单：")
    for i, (item, count) in enumerate(game_state['inventory'].items(), 1):
        if count > 0:
            print(f"{i}. {item}x{count}")

def get_item_desc(item):
    """道具说明"""
    desc = {
        '放大镜': "查看当前和下一发子弹",
        '刀': "下次实弹伤害翻倍",
        '啤酒': "恢复2HP",
        '饮料': "跳过2发子弹",
        '烟': "3回合减伤1点",
        '肾上腺素': "偷取敌人随机道具",
        '药': "25%+2HP/50%无效/25%-2HP",
        '手机': "查看指定位置子弹",
        '逆转器': "反转所有子弹类型"
    }
    return desc.get(item, "???")
def use_item():
    """道具使用系统"""
    items = list(game_state['inventory'].keys())
    print("\n=== 道具库 ===")
    for idx, (item, count) in enumerate(game_state['inventory'].items(), 1):
        print(f"{idx}. {item} x{count} | {get_item_desc(item)}")
    
    while True:
        try:
            choice = input("\n选择道具(1-8/0取消)：").strip()
            if choice == '0': return False
            choice = int(choice)-1
            if 0 <= choice < 8:
                item = items[choice]
                if game_state['inventory'][item] < 1:
                    print("道具不足！")
                    continue
                
                # 确认使用
                if input(f"使用{item}？(y)") != 'y':
                    continue
                
                game_state['inventory'][item] -= 1
                print(f"使用【{item}】！")
                
                # 处理效果
                if item == '放大镜':
                    current = game_state['chamber'][game_state['current_pos']]
                    next_pos = (game_state['current_pos']+1) % len(game_state['chamber'])
                    print(f"当前：{current}\n下个：{game_state['chamber'][next_pos]}")
                elif item == '刀':
                    game_state['knife_charged'] = True
                    print("下次实弹必暴击！")
                elif item == '啤酒':
                    game_state['player_hp'] = min(5, game_state['player_hp']+2)
                    print("HP+2！")
                elif item == '饮料':
                    game_state['current_pos'] = (game_state['current_pos']+2) % len(game_state['chamber'])
                    print("跳过2发！")
                elif item == '烟':
                    game_state['smoke_active'] = 3
                    print("获得3回合减伤！")
                elif item == '肾上腺素':
                    enemy_items = [k for k,v in game_state['inventory'].items() if v>0]
                    if enemy_items:
                        steal = random.choice(enemy_items)
                        game_state['inventory'][steal] += 1
                        game_state['inventory'][steal] -= 1
                        print(f"偷到{steal}！")
                elif item == '药':
                    res = random.choices(['+2','--','-2'], weights=[25,50,25])[0]
                    if res == '+2':
                        game_state['player_hp'] = min(5, game_state['player_hp']+2)
                        print("HP+2！")
                    elif res == '-2':
                        game_state['player_hp'] = max(0, game_state['player_hp']-2)
                        print("HP-2！")
                    else:
                        print("没有效果")
                elif item == '手机':
                    try:
                        pos = int(input(f"查看第几发(1-{len(game_state['chamber'])}:"))
                        if 1<=pos<=len(game_state['chamber']):
                            print(f"第{pos}发：{game_state['chamber'][pos-1]}")
                        else:
                            print("无效位置")
                    except:
                        print("输入错误")
                elif item == '逆转器':
                    game_state['chamber'] = ['实弹' if b=='空包弹' else '空包弹' for b in game_state['chamber']]
                    random.shuffle(game_state['chamber'])
                    print("子弹已反转！")
                
                input("按回车继续...")
                return True
            else:
                print("无效选择")
        except:
            print("输入错误")
def fire(attacker):
    """射击系统"""
    pos = game_state['current_pos']
    bullet = game_state['chamber'][pos]
    game_state['current_pos'] += 1
    
    print("\n枪膛：" + " ".join(f"{i+1}▮" if i==pos else "▯" for i in range(len(game_state['chamber']))))
    
    dmg = 0
    if bullet == '实弹':
        dmg = 2 if game_state['knife_charged'] else 1
        if attacker == 'player' and game_state['knife_charged']:
            game_state['knife_charged'] = False
    
    if attacker == 'enemy' and game_state['smoke_active'] > 0:
        dmg = max(0, dmg-1)
    
    if bullet == '实弹':
        if attacker == 'player':
            game_state['enemy_hp'] -= dmg
            print(f"造成{dmg}伤害！{'暴击！' if dmg==2 else ''}")
        else:
            game_state['player_hp'] -= dmg
            print(f"受到{dmg}伤害！")
    else:
        print("空包弹")
    
    if game_state['current_pos'] >= len(game_state['chamber']):
        print("\n弹药耗尽！")
        init_chamber()

def enemy_turn():
    """敌人AI"""
    print("\n=== 敌人行动 ===")
    if random.random() < 0.4:
        items = [k for k,v in game_state['inventory'].items() if v>0 and k not in ['肾上腺素','药','手机','逆转器']]
        if items:
            item = random.choice(items)
            game_state['inventory'][item] -= 1
            print(f"敌人使用{item}！")
            if item == '啤酒':
                game_state['enemy_hp'] = min(5, game_state['enemy_hp']+1)
            elif item == '烟':
                game_state['smoke_active'] = 2
            return
    fire('enemy')
def main():
    print("=== 恶魔轮盘赌 ===")
    print("规则：")
    print("- 道具上限12个 装弹自动补充")
    print("- 1使用道具 2开枪")
    init_chamber()
    
    while True:
        # 玩家回合
        while True:
            show_status()
            choice = input("\n行动：1道具 2开枪 > ")
            if choice == '1':
                if use_item():
                    continue
                else:
                    break
            elif choice == '2':
                fire('player')
                break
            else:
                print("输入1或2！")
        
        if game_state['enemy_hp'] <= 0:
            print("胜利！")
            break
        
        # 敌人回合
        game_state['smoke_active'] = max(0, game_state['smoke_active']-1)
        enemy_turn()
        if game_state['player_hp'] <= 0:
            print("失败...")
            break
        
        game_state['smoke_active'] = max(0, game_state['smoke_active']-1)

if __name__ == "__main__":
    main()