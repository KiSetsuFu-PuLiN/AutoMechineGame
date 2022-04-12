# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 14:28:47 2020

@author: echo
"""
import pygame,sys,numpy,os
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("元胞自动机")
screen_info=pygame.display.Info() 
screen=pygame.display.set_mode([screen_info.current_w,screen_info.current_h],pygame.FULLSCREEN)

#把这些安排在设置里
T_size=10#元胞大小
T_room=1#元胞间隙
T_radius=1#作用域半径
T_birth=[3,3]#诞生所需元胞数区间
T_live=[2,3]#存在所需元胞数区间
world_history_max_len=100#最大历史元胞状态记录数量
display_history=False#是否显示残影
history_color1=(200,0,0)#基本残影颜色
display_history_depth=4#残影层数
display_history_kind=False#是否使用残影x^(-1)衰变
display_T_Surface_side=True#是否显示T_Surface边框
advance_pause=False#是否开局暂停
ghost_color=(255,255,0)#鬼影颜色

skip_read_msg=False#是否跳过读取提示

#把这些安排在控制台里
T_update_time=1#元胞刷新帧间隔


#主界面
def main_UI():
    bo=pygame.mixer.Sound('bo.wav')
    bo.set_volume(1)
    selections_word=['开始','读取','选项','其他','退出']#选项
    selections_emoji=['( •̀ ω •́ )y','(o゜▽゜)o☆','ԅ(¯﹃¯ԅ)','(oﾟvﾟ)ノ','(இ௰இ)']
    pointer=0#主界面指针
    font_size=int(screen_info.current_h/18)#字体大小
    font=pygame.font.Font('font.ttf',font_size)#字体
    font_topic=pygame.font.Font('font.ttf',font_size*2)#主题字体
    #font_event=pygame.font.Font('font.ttf',int(font_size/2))#事件字体
    topic='元胞自动机'
    x=1.25#重点显示放大倍率
    topic_image=font_topic.render(topic,True,(255,255,255))
    selection_rects=[[] for i in range(len(selections_word))]
    y=x#样品元胞大小倍数
    z=10#样品元胞裂隙相对倍数
    size=y*font_size
    T_sample=[pygame.Surface((size,size)),pygame.Surface((size,size))]
    y6=size/3
    y6_room=y6/z
    for i in range(3):
        pygame.draw.rect(T_sample[0],(255,255,255),((i*y6,y6),(y6-y6_room,y6-y6_room)),0)
        pygame.draw.rect(T_sample[1],(255,255,255),((y6,i*y6),(y6-y6_room,y6-y6_room)),0)
    time=0
    time_max=10#变更时间
    index=0
    mouse_catch=False
    while True:
        screen.fill((0,0,0))
        selections=selections_word[:]
        selections[pointer]='%s %s'%(selections[pointer],selections_emoji[pointer])
        selection_images=[font.render(i,True,(255,255,255)) for i in selections]
        center=tuple(int(i) for i in (screen_info.current_w/2,screen_info.current_h/2))#中心参照位置
        pointer%=len(selections)
        
        #标题显示
        ls_rect=topic_image.get_rect()
        screen.blit(topic_image , (center[0]-ls_rect.width/2 , center[1]-ls_rect.height) )
        
        #选项显示
        line_room=int(1.5*font_size)
        line_start=screen_info.current_h/10#选项起始线距离中心点的距离
        for i in range(len(selection_images)):
            ls_rect=selection_images[i].get_rect()
            if i==pointer:#重点显示
                selection_images[i]=pygame.transform.smoothscale(selection_images[i],[int(i) for i in (x*ls_rect.width , x*ls_rect.height)])
                ls_rect=selection_images[i].get_rect()
                ls_rect2=selection_images[i].get_rect()
                if time>=time_max:
                    time=0
                    index+=1
                    index%=2
                for j in (-1,1):
                    screen.blit(T_sample[index],(center[0]+j*(ls_rect2.width/2+size)-size/2 , line_start+center[1]-size/2))
            
            selection_rects[i]=center[0]-ls_rect.width/2,center[1]+line_start-ls_rect.height/2
            screen.blit(selection_images[i] , selection_rects[i])
            line_start+=line_room
        for event in pygame.event.get():#事件处理
            if event.type==2:#按下按键
                bo.play()
                if event.unicode=='s' or event.key==274:
                    pointer+=1
                elif event.unicode=='w' or event.key==273:
                    pointer-=1
                elif event.unicode=='z' or event.key==13:
                    x=1
            elif event.type==3:#抬起按键
                if event.key==122 or event.key==13:
                    return pointer
            elif event.type==4:#鼠标移动
                mouse_catch=False
                for i in range(len(selections)):
                    ls_rect=selection_images[i].get_rect()
                    if (event.pos[0]<=ls_rect.right+selection_rects[i][0] and event.pos[0]>=ls_rect.left+selection_rects[i][0]) and (event.pos[1]>=ls_rect.top+selection_rects[i][1] and event.pos[1]<=ls_rect.bottom+selection_rects[i][1]):
                        mouse_catch=True
                        if pointer!=i:
                            bo.play()
                            pointer=i
            elif event.type==5:#鼠标按下
                if event.button==1:
                    for i in range(len(selections)):
                        ls_rect=selection_images[i].get_rect()
                        if (event.pos[0]<=ls_rect.right+selection_rects[i][0] and event.pos[0]>=ls_rect.left+selection_rects[i][0]) and (event.pos[1]>=ls_rect.top+selection_rects[i][1] and event.pos[1]<=ls_rect.bottom+selection_rects[i][1]):
                            bo.play()
                            x=1
            elif event.type==6:#鼠标抬起
                if mouse_catch:return pointer
                else:
                    x=1.25
        pygame.display.flip()
        time+=1

#游戏界面
def game_UI():
    time=0#计时器
    pause=advance_pause#砸瓦鲁多
    _exit=False#退出
    #音乐播放器
    music_player=pygame.mixer.music
    music_player.set_volume(1)
    music_player.set_endevent(25)
    music_player.stop()
    if display_history_kind:#残影x^(-1)衰变
        history_colors=[(history_color1[0]//(i+1),0,0) for i in range(display_history_depth)]
        history_colors.reverse()
    else:#残影线性衰变
        history_colors=[((i+1)*history_color1[0]//display_history_depth,0,0) for i in range(display_history_depth)]
    
    console_h_w=3#控制台高——宽比
    
    #控制台定义
    console_Surface_width=screen_info.current_h//console_h_w#控制台宽度
    #控制台按键设置
    console_font_size=console_Surface_width//10
    console_font_size_backup=console_font_size
    #控制台按键对象定义：
    class console_button():
        def __init__(self,text,center,is_button=False,x=1.25,function=lambda:None):
            self.fonts=[pygame.font.Font('font.ttf',int(i*console_font_size)) for i in (1,x)]
            self.text=text
            self.is_button=is_button
            self.images#跟随self.text变化，[0]和[1]分别为常规和大号
            self.center=tuple(int(i) for i in center)
            self.bigger=False
            self.function=function
        def draw(self):
            image=self.images[1] if self.bigger else self.images[0]
            rect=image.get_rect()
            rect.center=self.center
            screen.blit(image,rect)
        def __setattr__(self, name, value):
            object.__setattr__(self,name,value)
            if name=='text':#用于文本发生变化时的图像自动更新
                self.images=[font.render(value, True, (255,255,255)) for font in self.fonts]
    #按键定义        
    console_buttons=[]
    line=console_font_size
    def f():
        nonlocal world,world_backup_list,pause
        try:
            world_backup_end=world_backup_list.pop()
            for x in range(T_num_rect[0]):
                for y in range(T_num_rect[1]):
                    world[x][y][0]=world_backup_end[x][y]
            pause=True
        except IndexError:
            pass
    console_buttons.append(console_button('上一帧', (console_Surface_width/4,line),True,function=f))
    def f():
        nonlocal world,world_backup_list,pause,time
        pause=True
        #备份
        world_backup=numpy.array([[world[i][j][0] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])],dtype=bool)
        world_backup_list.append(world_backup)
        if len(world_backup_list)>world_history_max_len:
            del(world_backup_list[0])
        #(利用备份)演算新状态
        for x in range(T_num_rect[0]):
            for y in range(T_num_rect[1]):
                T_sround=0
                #检测周边元胞数
                for i in range(-T_radius,T_radius+1):
                    for j in range(-T_radius,T_radius+1):
                        if (i==0 and j==0) or x+i<0 or x+i>=T_num_rect[0] or y+j<0 or y+j>=T_num_rect[1]:
                            pass
                        elif world_backup[x+i][y+j]:
                            T_sround+=1
                if world_backup[x][y]:#生存法则
                    if T_sround<=T_live[1] and T_sround>=T_live[0]:
                        world[x][y][0]=True
                    else:
                        world[x][y][0]=False
                else:#诞生法则
                    if T_sround<=T_birth[1] and T_sround>=T_birth[0]:
                        world[x][y][0]=True
                    else:
                        world[x][y][0]=False
        #计时器重置
        time=0
    console_buttons.append(console_button('下一帧', (console_Surface_width*3/4,line),True,function=f))
    line+=console_font_size*2.5
    console_font_size*=2
    def f():
        nonlocal pause
        pause=not pause
        #时停按钮————console_button_time
    console_button_time=console_button('正在运行' if not pause else '砸瓦鲁多', (console_Surface_width/2,line),True,1.1,function=f)
    console_buttons.append(console_button_time) 
    line+=console_font_size
    console_font_size//=2
    line+=console_font_size
        #更新间隔帧数显示按钮————console_button_fps
    console_button_fps=console_button('更新间隔帧数:%d'%(T_update_time),(console_Surface_width/2,line))
    console_buttons.append(console_button_fps)
    def f():
        nonlocal console_button_fps
        global T_update_time
        if T_update_time>1:
            T_update_time-=1
        console_button_fps.text='更新间隔帧数:%d'%(T_update_time)
    console_buttons.append(console_button('<', (console_Surface_width/20,line),True,function=f))
    def f():
        nonlocal console_button_fps
        global T_update_time
        T_update_time+=1
        console_button_fps.text='更新间隔帧数:%d'%(T_update_time)
    console_buttons.append(console_button('>', (console_Surface_width*19/20,line),True,function=f))
    line+=console_font_size*3
    console_font_size*=1.5
    block_file_list=os.listdir('blocks/')
    block_list=['保存为块','删除元胞']#block_list[0]是添加块按键,block_list[1]是删除快捷键
    block_list.extend([os.path.splitext(i)[0] for i in block_file_list])
    block_list_pointer=0
    console_buttons.append(console_button('Block', (console_Surface_width/2,line)))
    def f():
        nonlocal block_list_pointer,console_button_blockname
        block_list_pointer-=1
        if block_list_pointer<0:
            block_list_pointer%=len(block_list)
        console_button_blockname.text=block_list[block_list_pointer]
    console_buttons.append(console_button('<', (console_Surface_width/8,line),True,function=f))
    def f():
        nonlocal block_list_pointer,console_button_blockname
        block_list_pointer+=1
        lenth=len(block_list)
        if block_list_pointer>=lenth:
            block_list_pointer%=lenth
        console_button_blockname.text=block_list[block_list_pointer]
    console_buttons.append(console_button('>', (console_Surface_width*7/8,line),True,function=f))
    line+=console_font_size
    #定义块预览窗口
    block_Surface_rect_width=console_Surface_width*9//10
    line+=block_Surface_rect_width//2
    block_Surface=pygame.Surface((block_Surface_rect_width,block_Surface_rect_width))
    block_Surface_rect=block_Surface.get_rect()
    block_Surface_rect.center=(console_Surface_width//2,line)
    block_function_list=[]#block图标绘制————[0]保存为块图标,[1]删除元胞图标,[2]显示预览
    block_0_image=pygame.Surface((block_Surface_rect_width,block_Surface_rect_width)).convert()
    pygame.draw.circle(block_0_image,(255,255,255),(block_Surface_rect_width//2,block_Surface_rect_width//2),block_Surface_rect_width*5//12,block_Surface_rect_width//40)
    pygame.draw.line(block_0_image,(255,255,255),(block_Surface_rect_width//4,block_Surface_rect_width//2),(block_Surface_rect_width*3//4,block_Surface_rect_width//2),block_Surface_rect_width//10)
    pygame.draw.line(block_0_image,(255,255,255),(block_Surface_rect_width//2,block_Surface_rect_width//4),(block_Surface_rect_width//2,block_Surface_rect_width*3//4),block_Surface_rect_width//10)
    block=[]#block[y][x]
    def f():
        block_Surface.blit(block_0_image,(0,0,block_Surface_rect_width,block_Surface_rect_width))
    block_function_list.append(f)
    def f():
        block_1_image=pygame.transform.rotate(block_0_image,45)
        rect=block_1_image.get_rect()
        rect.center=block_Surface_rect_width//2,block_Surface_rect_width//2
        block_Surface.blit(block_1_image,rect)
    block_function_list.append(f)
    def f():
        nonlocal block#block[y][x]
        block=[]
        with open('blocks/%s'%block_file_list[block_list_pointer-2],'rt',encoding='utf-8') as block_file:
            for line in block_file:
                block_line=[]
                block.append(block_line)
                for T in line:
                    if T=='〇':
                        block_line.append(False)
                    elif T=='壹':
                        block_line.append(True)
        num_rect=[len(block[0]),len(block)]
        num_lenth=num_rect[0] if num_rect[0]>num_rect[1] else num_rect[1]
        if num_lenth*(T_room+T_size)>=block_Surface_rect_width*9//10:
            T_size_now=(block_Surface_rect_width*9/10)//num_lenth-T_room
        else:
            T_size_now=T_size
        block_image=pygame.Surface((num_rect[0]*(T_room+T_size_now),num_rect[1]*(T_room+T_size_now)))
        for x in range(num_rect[0]):
            for y in range(num_rect[1]):
                if block[y][x]:
                    pygame.draw.rect(block_image,(255,255,255),(T_room+(T_room+T_size_now)*x,T_room+(T_room+T_size_now)*y,T_size_now,T_size_now),0)
        block_image_rect=block_image.get_rect()
        block_image_rect.center=block_Surface_rect_width//2,block_Surface_rect_width//2
        block_Surface.blit(block_image,block_image_rect)
    block_function_list.append(f)
    line+=block_Surface_rect_width//2
    console_font_size=console_font_size_backup
        #blockname显示按钮————console_button_blockname
    line+=console_font_size
    console_button_blockname=console_button(block_list[block_list_pointer], (console_Surface_width//2,line))
    console_buttons.append(console_button_blockname)
    #继续按键定义
    line+=console_font_size*2.5
        #歌曲控制按钮————console_button_music
    console_button_music_text_list='正在播放','播放控制器'
    music_play=True
    def f():
        nonlocal music_play,console_button_music
        if music_play:
            music_play=False
            console_button_music.text=console_button_music_text_list[1]
        else :
            music_play=True
            console_button_music.text=console_button_music_text_list[0]
    console_button_music=console_button(console_button_music_text_list[0], (console_Surface_width/2,line),True,1.1,function=f)
    console_buttons.append(console_button_music)
    console_font_size*=1.5
    #音乐播放
    music_list_pointer=0
    music_list_pointer_backup=music_list_pointer
    music_file_list=os.listdir('musics/')
    music_list=[os.path.splitext(i)[0] for i in music_file_list]
    music_player.load('musics/%s'%music_file_list[music_list_pointer])
    def f():
        nonlocal music_list_pointer,console_button_musicname
        music_list_pointer-=1
        if music_list_pointer<=0:
            music_list_pointer%=len(music_list)
    console_buttons.append(console_button('<', (console_Surface_width/7,line),True,function=f))
    def f():
        nonlocal music_list_pointer,console_button_musicname
        lenth=len(music_list)
        music_list_pointer+=1
        if music_list_pointer>=lenth:
            music_list_pointer%=lenth
    console_buttons.append(console_button('>', (console_Surface_width*6/7,line),True,function=f))
    console_font_size=console_font_size_backup
        #歌曲显示按钮————console_button_musicname
    line+=console_font_size*1.5
    console_button_musicname=console_button(music_list[music_list_pointer], (console_Surface_width/2,line))
    console_buttons.append(console_button_musicname)
    line=screen_info.current_h-console_font_size*2
    def f():
        window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//5))
        window_rect=window.get_rect()
        window_rect.center=screen_info.current_w//2,screen_info.current_h//2
        file_name=''#文件名（不含后缀）
        class Button(console_button):
            def draw(self):
                image=self.images[1] if self.bigger else self.images[0]
                rect=image.get_rect()
                rect.center=self.center
                window.blit(image,rect)
        button_list=[Button('另存为', (window_rect.width//2,window_rect.height//4)),\
                     Button('%s|'%file_name, (window_rect.width//2,window_rect.height//2)),\
                     Button('确定',(window_rect.width//4,window_rect.height*3//4),True),\
                     Button('取消',(window_rect.width*3//4,window_rect.height*3//4),True)]
        while True:
            for button in button_list:
                button.bigger=False
            mouse_button_cache=[False,None]
            cache_down=False#鼠标是否按下按钮
            key_down=False
            yes=False
            selected=False
            while True:
                for event in pygame.event.get():
                    if event.type==2:#keydown
                        if event.key==8:#退格键
                            index=len(file_name)-1
                            if not index<0:
                                file_name=file_name[:index]
                                button_list[1].text='%s|'%file_name
                        elif event.key==13:#回车
                            key_down=True
                            button_list[2].bigger=True
                            yes=True
                        else:
                            file_name='%s%s'%(file_name,event.unicode)
                            button_list[1].text='%s|'%file_name
                    elif event.type==3:#keyup
                        if event.key==13:
                            selected=True
                    elif event.type==4:#mouse_move
                        if not key_down:
                            mouse_button_cache=[False,None]
                            for button in button_list:
                                if button.is_button:
                                    button_rect=button.images[1 if button.bigger else 0].get_rect()
                                    if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                        mouse_button_cache=[True,button]
                                        if not cache_down:
                                            button.bigger=True
                                    else:
                                        button.bigger=False
                    elif event.type==5:#mouse_down
                        if mouse_button_cache[0] and not key_down:
                            mouse_button_cache[1].bigger=False
                            cache_down=True
                    elif event.type==6:#mouse_up
                        cache_down=False
                        if mouse_button_cache[0] and not key_down:
                            mouse_button_cache[1].bigger=True
                            selected=True
                            if button_list.index(mouse_button_cache[1])==2:
                                yes=True
                            else:
                                yes=False
                    elif event.type==12:#QUIT
                        sys.exit(0)
                #显示
                window.fill((0,0,0))
                pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                for button in button_list:
                    button.draw()
                screen.blit(window,window_rect)
                pygame.display.flip()
                if selected:
                    break
            #开始保存
            def save():#储存，成功则返回True，失败返回False
                file_full_name='%s.txt'%file_name
                file_list=os.listdir('saves/')
                if file_full_name in file_list:#存在同名文件
                    yes=False
                    selected=False
                    mouse_button_cache=[False,None]
                    mouse_down=False
                    class Button(console_button):
                        def draw(self):
                            image=self.images[1] if self.bigger else self.images[0]
                            rect=image.get_rect()
                            rect.center=self.center
                            window.blit(image,rect)
                    window=pygame.Surface((screen_info.current_w//2,screen_info.current_w//6))
                    window.fill((0,0,0))
                    window_rect=window.get_rect()
                    window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                    button_list=[Button('是否覆盖同名存档？', (window_rect.width//2,window_rect.height//3)),\
                                 Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                 Button('否[N]',(window_rect.width*3//4,window_rect.height*2//3),True)]
                    while True:#覆盖询问窗口
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                pass
                            elif event.type==3:#keyup
                                if event.key==121:#y
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                                    yes=True
                                    selected=True
                                else:
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                    selected=True
                            elif event.type==4:#mouse_move
                                mouse_button_cache=[False,None]
                                for button in button_list:
                                    if button.is_button:
                                        if button.bigger:
                                            button_rect=button.images[1].get_rect()
                                        else:
                                            button_rect=button.images[0].get_rect()
                                        button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                        if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                            mouse_button_cache[0]=True
                                            mouse_button_cache[1]=button
                                            if not mouse_down:
                                                mouse_button_cache[1].bigger=True
                                        else:
                                            button.bigger=False
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=False
                                else :
                                    for button in button_list[1:]:
                                        button.bigger=False
                                mouse_down=True
                            elif event.type==6:#mouse_up
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==1:
                                        yes=True
                                mouse_down=False
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        if selected:
                            break
                    if not yes:return False
                #开始存档
                try:
                    with open('saves/%s'%file_full_name,mode="wt",encoding="utf-8") as file:
                        file.write('<Ts>\n')
                        for y in range(T_num_rect[1]):
                            for x in range(T_num_rect[0]):
                                if world[x][y][0]:
                                    file.write('壹')
                                else:
                                    file.write('〇')
                            file.write('\n')
                        file.write('<Settings>\n')
                        file.writelines(['%s\n'%i for i in\
                                        ['T_size=%d'%T_size,\
                                         'T_room=%d'%T_room,\
                                         'T_radius=%d'%T_radius,\
                                         'T_birth=%s'%str(T_birth),\
                                         'T_live=%s'%str(T_live),\
                                         'world_history_max_len=%d'%world_history_max_len,\
                                         'display_history=%d'%int(display_history),\
                                         'history_color1=%s'%str(history_color1),\
                                         'display_history_depth=%d'%display_history_depth,\
                                         'display_history_kind=%d'%int(display_history_kind),\
                                         'display_T_Surface_side=%d'%int(display_T_Surface_side),\
                                         'advance_pause=%d'%int(advance_pause),\
                                         'ghost_color=%s'%str(ghost_color),\
                                         ]])
                except:
                    def error_window():
                        yes=False
                        key_cache=False
                        mouse_cache=False
                        class Button(console_button):
                            def draw(self):
                                image=self.images[1] if self.bigger else self.images[0]
                                rect=image.get_rect()
                                rect.center=self.center
                                window.blit(image,rect)
                        window=pygame.Surface((screen_info.current_w*3//8,screen_info.current_w//6))
                        window_rect=window.get_rect()
                        window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                        button_list=[Button('存档创建失败', (window_rect.width//2,window_rect.height//4)),\
                                     Button('请不要使用非法字符创建存档', (window_rect.width//2,window_rect.height//2)),\
                                     Button('[知道了]', (window_rect.width//2,window_rect.height*3//4),True)]
                        while True:#文件创建失败提示窗口
                            for event in pygame.event.get():
                                if event.type==2:
                                    button_list[2].bigger=True
                                    key_cache=True
                                elif event.type==3:
                                    button_list[2].bigger=False
                                    key_cache=False
                                    yes=True
                                elif event.type==4:
                                    if not (key_cache and mouse_cache):
                                        button=button_list[2]
                                        button_rect=button.images[1 if button.bigger else 0].get_rect()
                                        if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                            button.bigger=True
                                        else:
                                            button.bigger=False
                                elif event.type==5:
                                    if not key_cache:
                                        if button_list[2].bigger:
                                            button_list[2].bigger=False
                                            mouse_cache=True
                                elif event.type==6:
                                    if mouse_cache:
                                        button_list[2].bigger=True
                                        yes=True
                                elif event.type==12:
                                    sys.exit(0)
                            window.fill((0,0,0))
                            pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                            for button in button_list:
                                button.draw()
                            screen.blit(window,window_rect)
                            pygame.display.flip()
                            if yes:
                                return
                    error_window()
                    return False
                return True
            if yes:
                if save():
                    break
            else:
                break
    '''哼哼，啊啊啊啊啊啊啊啊啊啊啊啊，啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊'''
    console_buttons.append(console_button('保存', (console_Surface_width/4,line),True,function=f))
    def f():
        nonlocal _exit
        class Button(console_button):
            def draw(self):
                image=self.images[1] if self.bigger else self.images[0]
                rect=image.get_rect()
                rect.center=self.center
                window.blit(image,rect)
        yes=False
        window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//6))
        window_rect=window.get_rect()
        pygame.draw.rect(window,(255,255,255),window_rect,6)
        window_rect.center=screen.get_rect().center
        button_list=[Button('确定要退出吗？',(window_rect.width//2,window_rect.height//3),False),\
                     Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                     Button('否[N]', (window_rect.width*3//4,window_rect.height*2//3),True)]
        for button in button_list[1:]:
            button.bigger=True
        mouse_button_cache=[False,None]
        while True:#退出询问事件
            window.fill((0,0,0))
            pygame.draw.rect(window,(255,255,255),(0,0,window_rect[2],window_rect[3]),6)
            selected=False
            for event in pygame.event.get():
                if event.type==2:#keydown
                    if event.key==121:#y
                        button_list[1].bigger=False
                        button_list[2].bigger=True
                    else:
                        button_list[1].bigger=True
                        button_list[2].bigger=False
                elif event.type==3:#keyup
                    if event.key==121:#y
                        button_list[1].bigger=True
                        button_list[2].bigger=False
                        yes=True
                        selected=True
                    else:
                        button_list[1].bigger=False
                        button_list[2].bigger=True
                        selected=True
                elif event.type==4:#mouse_move
                    mouse_button_cache=[False,None]
                    for button in button_list:
                        if button.is_button:
                            if button.bigger:
                                button_rect=button.images[1].get_rect()
                            else:
                                button_rect=button.images[0].get_rect()
                            button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                            if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                mouse_button_cache[0]=True
                                mouse_button_cache[1]=button
                            else:
                                button.bigger=True
                elif event.type==5:#mouse_down
                    if mouse_button_cache[0]:
                        mouse_button_cache[1].bigger=False
                    else :
                        for button in button_list[1:]:
                            button.bigger=True
                elif event.type==6:#mouse_up
                    if mouse_button_cache[0]:
                        mouse_button_cache[1].bigger=True
                        selected=True
                        if button_list.index(mouse_button_cache[1])==1:
                            yes=True
                elif event.type==12:#QUIT
                    sys.exit(0)
            for button in button_list:
                button.draw()
            screen.blit(window,window_rect)
            pygame.display.flip()
            if selected:
                break
        if yes:
            _exit=True
        return
    console_buttons.append(console_button('退出', (console_Surface_width*3/4,line),True,function=f))
    
    #元胞世界定义
    T_Surface_bigrect=((console_Surface_width,0),(screen_info.current_w-console_Surface_width,screen_info.current_h))
    T_num_rect=(T_Surface_bigrect[1][0]//(T_size+T_room),T_Surface_bigrect[1][1]//(T_size+T_room))
    T_Surface_room=(T_Surface_bigrect[1][0]%(T_size+T_room),T_Surface_bigrect[1][1]%(T_size+T_room))
    T_Surface_rect=((T_Surface_room[0]//2+console_Surface_width,T_Surface_room[1]//2) , (T_num_rect[0]*(T_room+T_size),T_num_rect[1]*(T_room+T_size)) )
    #要求：输出元胞的时候先输出空隙
    T_Surface=pygame.Surface(T_Surface_rect[1])#元胞画布
    #T_Surface_rect[0]是绘制元胞画布的起始点
    world=[[[False,T_room+i*(T_room+T_size),T_room+j*(T_room+T_size)] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])]
    #world[x_num][y_num][0——状态，1——x位置，2——y位置]
    world_backup_list=[]#用来堆叠历史状态
    world_mouse_down_up_tuple=[False,False,[0,0],[0,0],False]#[0]是否按下,[1]是否抬起(GO!)，[2]终点坐标，[3]起点坐标，[4]是否处于元胞画布
    
    while True:
        
        #音乐播放
        if music_list_pointer != music_list_pointer_backup:#老板换碟！
            music_list_pointer_backup=music_list_pointer
            music_player.load('musics/%s'%music_file_list[music_list_pointer])
            console_button_musicname.text=music_list[music_list_pointer]
        if music_play:
            if not music_player.get_busy():
                music_player.play()
            else:
                music_player.unpause()
        else:
            music_player.pause()
        
        #显示
        screen.fill((0,0,0))
        #控制台显示
        for button in console_buttons:
            button.draw()
        #block预览显示
        block_Surface.fill((0,0,0))
        if block_list_pointer<2:
            block_function_list[block_list_pointer]()
        else:
            block_function_list[2]()
        pygame.draw.rect(block_Surface,(255,255,255),((0,0),(block_Surface_rect_width,block_Surface_rect_width)),1)
        screen.blit(block_Surface,block_Surface_rect)
        #元胞画布显示
        if display_T_Surface_side:pygame.draw.polygon(screen,(255,255,255),((T_Surface_rect[0][0]-1,0),(T_Surface_rect[0][0]-1,screen_info.current_h)),1)
        T_Surface.fill((0,0,0))
        if display_history:#残影显示
            history_len=len(world_backup_list)
            for i in range(display_history_depth):
                world_backup_list_index=history_len-display_history_depth+i
                if world_backup_list_index<0:
                    continue
                else:
                    for x in range(T_num_rect[0]):
                        for y in range(T_num_rect[1]):
                            if world_backup_list[world_backup_list_index][x][y]:
                                pygame.draw.rect(T_Surface, history_colors[i], ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
        if world_mouse_down_up_tuple[4]:#鬼影显示
            if block_list_pointer==0:#保存为块
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        pygame.draw.rect(T_Surface,ghost_color, ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
            elif block_list_pointer==1:#删除元胞
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        pygame.draw.rect(T_Surface,ghost_color, ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
            else:#写入块
                def f(x0,xt,y0,yt):#象限判断
                    if xt>=x0 and yt>=y0:
                        return 4
                    elif xt>=x0 and yt<y0:
                        return 1
                    elif xt<x0 and yt<y0:
                        return 2
                    else:
                        return 3
                angle=f(world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                block_rect=len(block[0]),len(block)
                if angle==1:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+y,world_mouse_down_up_tuple[3][1]-x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==2:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-x,world_mouse_down_up_tuple[3][1]-y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==3:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-y,world_mouse_down_up_tuple[3][1]+x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==4:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+x,world_mouse_down_up_tuple[3][1]+y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
        for x in range(T_num_rect[0]):#元胞显示
            for y in range(T_num_rect[1]):
                if world[x][y][0]:
                    pygame.draw.rect(T_Surface,(255,255,255), ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
        screen.blit(T_Surface,T_Surface_rect[0])
        #最终显示
        pygame.display.flip()
        
        mouse_once_up=False
        for event in pygame.event.get():#事件处理
            if event.type==1:#application_event
                pass
            elif event.type==2:#keydown
                if event.key==27:#ESC
                    ESC_Onece=True#是第一次按下ESC键
                    class Button(console_button):
                        def draw(self):
                            image=self.images[1] if self.bigger else self.images[0]
                            rect=image.get_rect()
                            rect.center=self.center
                            window.blit(image,rect)
                    yes=False
                    window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//6))
                    window_rect=window.get_rect()
                    pygame.draw.rect(window,(255,255,255),window_rect,6)
                    window_rect.center=screen.get_rect().center
                    button_list=[Button('确定要退出吗？',(window_rect.width//2,window_rect.height//3),False),\
                                 Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                 Button('否[N]', (window_rect.width*3//4,window_rect.height*2//3),True)]
                    for button in button_list[1:]:
                            button.bigger=True
                    mouse_button_cache=[False,None]
                    while True:#退出询问事件
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect[2],window_rect[3]),6)
                        selected=False
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                if event.key==121:#y
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                else:
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                            elif event.type==3:#keyup
                                if event.key==121:#y
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                                    yes=True
                                    selected=True
                                elif event.key==27:#esc
                                    if ESC_Onece:#取消第一次的esc抬起判断
                                        ESC_Onece=False
                                    else:
                                        button_list[1].bigger=False
                                        button_list[2].bigger=True
                                        selected=True
                                else:
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                    selected=True
                            elif event.type==4:#mouse_move
                                mouse_button_cache=[False,None]
                                for button in button_list:
                                    if button.is_button:
                                        if button.bigger:
                                            button_rect=button.images[1].get_rect()
                                        else:
                                            button_rect=button.images[0].get_rect()
                                        button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                        if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                            mouse_button_cache[0]=True
                                            mouse_button_cache[1]=button
                                        else:button.bigger=True
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=False
                                else :
                                    for button in button_list[1:]:
                                        button.bigger=True
                            elif event.type==6:#mouse_up
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==1:
                                        yes=True
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        if selected:
                            break
                    if yes:
                        _exit=True
                elif event.key==32:#Space
                    pause=not pause
            elif event.type==3:#keyup
                pass
            elif event.type==4:#mouse_move
                mouse_button_cache=[False,None]#用于判断鼠标是否被按键捕捉,捕捉的哪个键
                if event.pos[0]<=console_Surface_width:#鼠标处于控制台时
                    world_mouse_down_up_tuple[4]=False
                    for button in console_buttons:
                        if button.is_button:#如果是个按钮
                            if not button.bigger:
                                rect=button.images[0].get_rect()
                                rect.center=button.center
                                if rect.left<=event.pos[0] and rect.right>=event.pos[0] and rect.top<=event.pos[1] and rect.bottom>=event.pos[1]:
                                    button.bigger=True
                                    mouse_button_cache[0]=True
                                    mouse_button_cache[1]=button
                                else:
                                    button.bigger=False
                            else:
                                rect=button.images[1].get_rect()
                                rect.center=button.center
                                if not (rect.left<=event.pos[0] and rect.right>=event.pos[0] and rect.top<=event.pos[1] and rect.bottom>=event.pos[1]):
                                    button.bigger=False
                                else:
                                    button.bigger=True
                                    mouse_button_cache[0]=True
                                    mouse_button_cache[1]=button
                else:#鼠标处于元胞世界时
                    for button in console_buttons:#控制台按钮大小矫正
                        button.bigger=False
                    world_mouse_down_up_tuple[4]=True
                    for x in range(T_num_rect[0]+1):
                        if x==T_num_rect[0]:
                            world_mouse_down_up_tuple[2][0]=x-1
                        elif T_Surface_rect[0][0]+world[x][0][1]>event.pos[0]:
                            world_mouse_down_up_tuple[2][0]=x-1 if x>0 else 0
                            break
                    for y in range(T_num_rect[1]+1):
                        if y==T_num_rect[1]:
                            world_mouse_down_up_tuple[2][1]=y-1
                        elif T_Surface_rect[0][1]+world[0][y][2]>event.pos[1]:
                            world_mouse_down_up_tuple[2][1]=y-1 if y>0 else 0
                            break
                    if (not world_mouse_down_up_tuple[0]) and (not mouse_once_up):#如果鼠标没有按下
                        world_mouse_down_up_tuple[3]=world_mouse_down_up_tuple[2][:]
            elif event.type==5:#mouse_down
                if mouse_button_cache[0]:
                    mouse_button_cache[1].bigger=False
                else:#鼠标处于元胞世界时
                    world_mouse_down_up_tuple[4]=True
                    world_mouse_down_up_tuple[0]=True
                    world_mouse_down_up_tuple[1]=False
            elif event.type==6:#mouse_up
                if mouse_button_cache[0]:
                    mouse_button_cache[1].bigger=True
                    mouse_button_cache[1].function()
                else:#鼠标处于元胞世界时
                    world_mouse_down_up_tuple[4]=True
                    world_mouse_down_up_tuple[0]=False
                    world_mouse_down_up_tuple[1]=True
                    mouse_once_up=True
            elif event.type==12:#QUIT
                sys.exit(0)
            elif event.type==25:#音乐播放完毕
                music_list_pointer+=1
                lenth=len(music_list)
                if music_list_pointer>=lenth:
                    music_list_pointer%=lenth
        
        #元胞状态更新
        if time>=T_update_time:
            #备份
            world_backup=numpy.array([[world[i][j][0] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])],dtype=bool)
            world_backup_list.append(world_backup)
            if len(world_backup_list)>world_history_max_len:
                del(world_backup_list[0])
            #(利用备份)演算新状态
            for x in range(T_num_rect[0]):
                for y in range(T_num_rect[1]):
                    T_sround=0
                    #检测周边元胞数
                    for i in range(-T_radius,T_radius+1):
                        for j in range(-T_radius,T_radius+1):
                            if (i==0 and j==0) or x+i<0 or x+i>=T_num_rect[0] or y+j<0 or y+j>=T_num_rect[1]:
                                pass
                            elif world_backup[x+i][y+j]:
                                T_sround+=1
                    if world_backup[x][y]:#生存法则
                        if T_sround<=T_live[1] and T_sround>=T_live[0]:
                            world[x][y][0]=True
                        else:
                            world[x][y][0]=False
                    else:#诞生法则
                        if T_sround<=T_birth[1] and T_sround>=T_birth[0]:
                            world[x][y][0]=True
                        else:
                            world[x][y][0]=False
            #计时器重置
            time=0

        if world_mouse_down_up_tuple[1] and world_mouse_down_up_tuple[4]:#鬼影实现
            if block_list_pointer==0:#保存为块
                #保存窗口
                window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//5))
                window_rect=window.get_rect()
                window_rect.center=screen_info.current_w//2,screen_info.current_h//2
                file_name=''#文件名（不含后缀）
                class Button(console_button):
                    def draw(self):
                        image=self.images[1] if self.bigger else self.images[0]
                        rect=image.get_rect()
                        rect.center=self.center
                        window.blit(image,rect)
                button_list=[Button('Block另存为', (window_rect.width//2,window_rect.height//4)),\
                             Button('%s|'%file_name, (window_rect.width//2,window_rect.height//2)),\
                             Button('确定',(window_rect.width//4,window_rect.height*3//4),True),\
                             Button('取消',(window_rect.width*3//4,window_rect.height*3//4),True)]
                while True:
                    for button in button_list:
                        button.bigger=False
                    mouse_button_cache=[False,None]
                    cache_down=False#鼠标是否按下按钮
                    key_down=False
                    yes=False
                    selected=False
                    while True:
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                if event.key==8:#退格键
                                    index=len(file_name)-1
                                    if not index<0:
                                        file_name=file_name[:index]
                                        button_list[1].text='%s|'%file_name
                                elif event.key==13:#回车
                                    key_down=True
                                    button_list[2].bigger=True
                                    yes=True
                                else:
                                    file_name='%s%s'%(file_name,event.unicode)
                                    button_list[1].text='%s|'%file_name
                            elif event.type==3:#keyup
                                if event.key==13:
                                    selected=True
                            elif event.type==4:#mouse_move
                                if not key_down:
                                    mouse_button_cache=[False,None]
                                    for button in button_list:
                                        if button.is_button:
                                            button_rect=button.images[1 if button.bigger else 0].get_rect()
                                            if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                                mouse_button_cache=[True,button]
                                                if not cache_down:
                                                    button.bigger=True
                                            else:
                                                button.bigger=False
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0] and not key_down:
                                    mouse_button_cache[1].bigger=False
                                    cache_down=True
                            elif event.type==6:#mouse_up
                                cache_down=False
                                if mouse_button_cache[0] and not key_down:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==2:
                                        yes=True
                                    else:
                                        yes=False
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        #显示
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        if selected:
                            break
                    #开始保存
                    def save():#储存，成功则返回True，失败返回False
                        file_full_name='%s.txt'%file_name
                        file_list=os.listdir('blocks/')
                        if file_full_name in file_list:#存在同名文件
                            yes=False
                            selected=False
                            mouse_button_cache=[False,None]
                            mouse_down=False
                            class Button(console_button):
                                def draw(self):
                                    image=self.images[1] if self.bigger else self.images[0]
                                    rect=image.get_rect()
                                    rect.center=self.center
                                    window.blit(image,rect)
                            window=pygame.Surface((screen_info.current_w//2,screen_info.current_w//6))
                            window.fill((0,0,0))
                            window_rect=window.get_rect()
                            window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                            button_list=[Button('是否覆盖同名存档？', (window_rect.width//2,window_rect.height//3)),\
                                         Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                         Button('否[N]',(window_rect.width*3//4,window_rect.height*2//3),True)]
                            while True:#覆盖询问窗口
                                window.fill((0,0,0))
                                pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                                for button in button_list:
                                    button.draw()
                                screen.blit(window,window_rect)
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type==2:#keydown
                                        pass
                                    elif event.type==3:#keyup
                                        if event.key==121:#y
                                            button_list[1].bigger=True
                                            button_list[2].bigger=False
                                            yes=True
                                            selected=True
                                        else:
                                            button_list[1].bigger=False
                                            button_list[2].bigger=True
                                            selected=True
                                    elif event.type==4:#mouse_move
                                        mouse_button_cache=[False,None]
                                        for button in button_list:
                                            if button.is_button:
                                                if button.bigger:
                                                    button_rect=button.images[1].get_rect()
                                                else:
                                                    button_rect=button.images[0].get_rect()
                                                button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                                if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                                    mouse_button_cache[0]=True
                                                    mouse_button_cache[1]=button
                                                    if not mouse_down:
                                                        mouse_button_cache[1].bigger=True
                                                else:
                                                    button.bigger=False
                                    elif event.type==5:#mouse_down
                                        if mouse_button_cache[0]:
                                            mouse_button_cache[1].bigger=False
                                        else :
                                            for button in button_list[1:]:
                                                button.bigger=False
                                        mouse_down=True
                                    elif event.type==6:#mouse_up
                                        if mouse_button_cache[0]:
                                            mouse_button_cache[1].bigger=True
                                            selected=True
                                            if button_list.index(mouse_button_cache[1])==1:
                                                yes=True
                                        mouse_down=False
                                    elif event.type==12:#QUIT
                                        sys.exit(0)
                                if selected:
                                    break
                            if not yes:return False
                        #开始存档
                        try:
                            with open('blocks/%s'%file_full_name,mode="wt",encoding="utf-8") as file:
                                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                                buff=[]
                                for y in range(y0,yt+1):
                                    line=[]
                                    buff.append(line)
                                    for x in range(x0,xt+1):
                                        if world[x][y][0]:
                                            line.append('壹')
                                        else:
                                            line.append('〇')
                                #buff裁剪
                                delete_line_index=[0,0]#[0][1]表示上下实体数
                                for  i in range(len(buff)):
                                    if '壹' in buff[i]:
                                        delete_line_index[0]=i
                                        break
                                for i in reversed(range(len(buff))):
                                    if '壹' in buff[i]:
                                        delete_line_index[1]=i
                                        break
                                buff=buff[delete_line_index[0]:delete_line_index[1]+1]
                                while True:
                                    stop=False
                                    for line in buff:
                                        try:
                                            if line[0]=='壹':
                                                stop=True
                                        except IndexError:
                                            stop=True
                                    if stop:
                                        break
                                    else:
                                        for line in buff:
                                            del line[0]
                                while True:
                                    stop=False
                                    for line in buff:
                                        try:
                                            if line[-1]=='壹':
                                                stop=True
                                        except IndexError:
                                            stop=True
                                    if stop:
                                        break
                                    else:
                                        for line in buff:
                                            line.pop()
                                for line in buff:
                                    for char in line:
                                        file.write(char)
                                    file.write('\n')
                        except:
                            def error_window():
                                yes=False
                                key_cache=False
                                mouse_cache=False
                                class Button(console_button):
                                    def draw(self):
                                        image=self.images[1] if self.bigger else self.images[0]
                                        rect=image.get_rect()
                                        rect.center=self.center
                                        window.blit(image,rect)
                                window=pygame.Surface((screen_info.current_w*3//8,screen_info.current_w//6))
                                window_rect=window.get_rect()
                                window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                                button_list=[Button('Block创建失败', (window_rect.width//2,window_rect.height//4)),\
                                             Button('请不要使用非法字符创建Block', (window_rect.width//2,window_rect.height//2)),\
                                             Button('[知道了]', (window_rect.width//2,window_rect.height*3//4),True)]
                                while True:#文件创建失败提示窗口
                                    for event in pygame.event.get():
                                        if event.type==2:
                                            button_list[2].bigger=True
                                            key_cache=True
                                        elif event.type==3:
                                            button_list[2].bigger=False
                                            key_cache=False
                                            yes=True
                                        elif event.type==4:
                                            if not (key_cache and mouse_cache):
                                                button=button_list[2]
                                                button_rect=button.images[1 if button.bigger else 0].get_rect()
                                                if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                                    button.bigger=True
                                                else:
                                                    button.bigger=False
                                        elif event.type==5:
                                            if not key_cache:
                                                if button_list[2].bigger:
                                                    button_list[2].bigger=False
                                                    mouse_cache=True
                                        elif event.type==6:
                                            if mouse_cache:
                                                button_list[2].bigger=True
                                                yes=True
                                        elif event.type==12:
                                            sys.exit(0)
                                    window.fill((0,0,0))
                                    pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                                    for button in button_list:
                                        button.draw()
                                    screen.blit(window,window_rect)
                                    pygame.display.flip()
                                    if yes:
                                        return
                            error_window()
                            return False
                        return True
                    if yes:
                        if save():
                            break
                    else:
                        break
                #列表更新
                block_file_list=os.listdir('blocks/')
                block_list=['保存为块','删除元胞']
                block_list.extend([os.path.splitext(i)[0] for i in block_file_list])
            elif block_list_pointer==1:#删除元胞
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        world[x][y][0]=False
            else:#写入元胞
                def f(x0,xt,y0,yt):#象限判断
                    if xt>=x0 and yt>=y0:
                        return 4
                    elif xt>=x0 and yt<y0:
                        return 1
                    elif xt<x0 and yt<y0:
                        return 2
                    else:
                        return 3
                angle=f(world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                block_rect=len(block[0]),len(block)
                if angle==1:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+y,world_mouse_down_up_tuple[3][1]-x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==2:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-x,world_mouse_down_up_tuple[3][1]-y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==3:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-y,world_mouse_down_up_tuple[3][1]+x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==4:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+x,world_mouse_down_up_tuple[3][1]+y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
            #必要后缀步骤
            world_mouse_down_up_tuple[3]=world_mouse_down_up_tuple[2][:]
            world_mouse_down_up_tuple[1]=False
        if not pause:
            time+=1
            console_button_time.text='正在运行'
        else:console_button_time.text='砸瓦鲁多'
        if _exit:
            if music_player.get_busy():
                music_player.fadeout(10000)
            return
        
#读取界面
def read_UI():
    font_size=screen_info.current_w/40
    class Message_Button():
        def __init__(self,text,center,is_button=False,x=1.25,function=lambda:None):
            self.bigger=False
            self.fonts=[pygame.font.Font('font.ttf',int(i*font_size)) for i in (1,x)]
            self.text=text
            self.is_button=is_button
            self.images#跟随self.text变化，[0]和[1]分别为常规和大号
            self.image
            self.center=tuple(int(i) for i in center)
            self.function=function
        def draw(self):
            rect=self.image.get_rect()
            rect.center=self.center
            screen.blit(self.image,rect)
        def __setattr__(self, name, value):
            object.__setattr__(self,name,value)
            if name=='text':#用于文本发生变化时的图像自动更新
                self.images=[font.render(value, True, (255,255,255)) for font in self.fonts]
        def __getattribute__(self,name):
            if name=='image':
                return self.images[1 if self.bigger else 0]
            else: return object.__getattribute__(self, name)
    def message(text):
        main_message=Message_Button(text,(screen_info.current_w//2,font_size*6))
        then_message=Message_Button('按任意键继续......',(screen_info.current_w//2,screen_info.current_h*2//3))
        while True:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type==12:
                    sys.exit(0)
                elif event.type==2:
                    then_message.bigger=True
                elif event.type==3:
                    return
                elif event.type==5:
                    then_message.bigger=True
                elif event.type==6:
                    return
            main_message.draw()
            then_message.draw()
            pygame.display.flip()
    global skip_read_msg
    if not skip_read_msg:
        message('因为作者实在是肝不动了。。。')
        message('所以就做了个简单点的界面凑合着用吧(/ω＼*)')
        message('只能用键盘操作哦ο(=•ω＜=)ρ⌒☆')
        skip_read_msg=True
    
    def select(text):
        main_message=Message_Button('读取存档:%s'%os.path.splitext(text)[0],(screen_info.current_w//2,font_size*6))
        last_message=Message_Button('上一个(A)',(screen_info.current_w//4,screen_info.current_h*2//3))
        this_message=Message_Button('确定(S)',(screen_info.current_w//2,screen_info.current_h*2//3))
        next_message=Message_Button('下一个(D)',(screen_info.current_w*3//4,screen_info.current_h*2//3))
        while True:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type==12:
                    sys.exit(0)
                elif event.type==2:
                    if event.key== 115:#S
                        this_message.bigger=True
                    elif event.key== 97:#A
                        last_message.bigger=True
                    elif event.key== 100:#D
                        next_message.bigger=True
                elif event.type==3:
                    if event.key== 115:#S
                        return 'S'
                    elif event.key== 97:#A
                        return 'A'
                    elif event.key== 100:#D
                        return 'D'
            main_message.draw()
            last_message.draw()
            this_message.draw()
            next_message.draw()
            pygame.display.flip()
    save_file_list=os.listdir('saves/')
    if save_file_list==[]:
        message('没有存档可以读取哦~(￣▽￣* )ゞ')
        return
    save_file_list_pointer=0
    save_file_list_len=len(save_file_list)
    while True:
        selection=select(save_file_list[save_file_list_pointer])
        if selection=='A':
            save_file_list_pointer-=1
        elif selection=='D':
            save_file_list_pointer+=1
        elif selection=='S':
            break
        if save_file_list_pointer<0 or save_file_list_pointer>=save_file_list_len:
            save_file_list_pointer%=save_file_list_len
    def read_setting_msg():
        main_message=Message_Button('是否读取该存档所保存的设置？',(screen_info.current_w//2,font_size*6))
        yes_message=Message_Button('是[Y]',(screen_info.current_w//4,screen_info.current_h*2//3))
        no_message=Message_Button('否[n]',(screen_info.current_w*3//4,screen_info.current_h*2//3))
        while True:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type==12:
                    sys.exit(0)
                elif event.type==2:
                    if event.key== 110:#n
                        no_message.bigger=True
                    else:
                        yes_message.bigger=True
                elif event.type==3:
                    if event.key== 110:#n
                        return False
                    else :
                        return True
            main_message.draw()
            yes_message.draw()
            no_message.draw()
            pygame.display.flip()
    if read_setting_msg():
        global T_size,T_room,T_radius,T_birth,T_live,world_history_max_len,display_history,history_color1,display_history_depth,display_history_kind,display_T_Surface_side,advance_pause,ghost_color
        read_setting=True
    else:
        read_setting=False
    file=open('saves/%s'%save_file_list[save_file_list_pointer],'rt',encoding='utf-8')
    world_save=[]#[n]表示第n行
    save_pointer=0
    for line in file:
        if line=='<Ts>\n':
            save_pointer=0
            continue
        if line=='<Settings>\n':
            if read_setting:
                save_pointer=1
                continue
            else :
                break
        if save_pointer==0:#处理元胞
            world_save.append(line.rstrip())
        elif save_pointer==1:#处理设置
            name,value=line.rstrip().split('=',1)
            if name=='T_size':
                T_size=int(value)
            elif name=='T_room':
                T_room=int(value)
            elif name=='T_radius':
                T_radius=int(value)
            elif name=='T_birth':
                T_birth=[int(i) for i in value.strip('[]').split(',',1)]
            elif name=='T_live':
                T_live=[int(i) for i in value.strip('[]').split(',',1)]
            elif name=='world_history_max_len':
                world_history_max_len=int(value)
            elif name=='display_history':
                display_history=False if value=='0' else True
            elif name=='history_color1':
                history_color1=tuple(int(i) for i in value.strip('()').split(',',2))
            elif name=='display_history_depth':
                display_history_depth=int(value)
            elif name=='display_history_kind':
                display_history_kind=False if value=='0' else True
            elif name=='display_T_Surface_side':
                display_T_Surface_side=False if value=='0' else True
            elif name=='advance_pause':
                advance_pause=False if value=='0' else True
            elif name=='ghost_color':
                ghost_color=tuple(int(i) for i in value.strip('()').split(',',2))
    file.close()
    time=0#计时器
    pause=advance_pause#砸瓦鲁多
    _exit=False#退出
    #音乐播放器
    music_player=pygame.mixer.music
    music_player.set_volume(1)
    music_player.set_endevent(25)
    music_player.stop()
    if display_history_kind:#残影x^(-1)衰变
        history_colors=[(history_color1[0]//(i+1),0,0) for i in range(display_history_depth)]
        history_colors.reverse()
    else:#残影线性衰变
        history_colors=[((i+1)*history_color1[0]//display_history_depth,0,0) for i in range(display_history_depth)]
    
    console_h_w=3#控制台高——宽比
    
    #控制台定义
    console_Surface_width=screen_info.current_h//console_h_w#控制台宽度
    #控制台按键设置
    console_font_size=console_Surface_width//10
    console_font_size_backup=console_font_size
    #控制台按键对象定义：
    class console_button():
        def __init__(self,text,center,is_button=False,x=1.25,function=lambda:None):
            self.fonts=[pygame.font.Font('font.ttf',int(i*console_font_size)) for i in (1,x)]
            self.text=text
            self.is_button=is_button
            self.images#跟随self.text变化，[0]和[1]分别为常规和大号
            self.center=tuple(int(i) for i in center)
            self.bigger=False
            self.function=function
        def draw(self):
            image=self.images[1] if self.bigger else self.images[0]
            rect=image.get_rect()
            rect.center=self.center
            screen.blit(image,rect)
        def __setattr__(self, name, value):
            object.__setattr__(self,name,value)
            if name=='text':#用于文本发生变化时的图像自动更新
                self.images=[font.render(value, True, (255,255,255)) for font in self.fonts]
    #按键定义        
    console_buttons=[]
    line=console_font_size
    def f():
        nonlocal world,world_backup_list,pause
        try:
            world_backup_end=world_backup_list.pop()
            for x in range(T_num_rect[0]):
                for y in range(T_num_rect[1]):
                    world[x][y][0]=world_backup_end[x][y]
            pause=True
        except IndexError:
            pass
    console_buttons.append(console_button('上一帧', (console_Surface_width/4,line),True,function=f))
    def f():
        nonlocal world,world_backup_list,pause,time
        pause=True
        #备份
        world_backup=numpy.array([[world[i][j][0] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])],dtype=bool)
        world_backup_list.append(world_backup)
        if len(world_backup_list)>world_history_max_len:
            del(world_backup_list[0])
        #(利用备份)演算新状态
        for x in range(T_num_rect[0]):
            for y in range(T_num_rect[1]):
                T_sround=0
                #检测周边元胞数
                for i in range(-T_radius,T_radius+1):
                    for j in range(-T_radius,T_radius+1):
                        if (i==0 and j==0) or x+i<0 or x+i>=T_num_rect[0] or y+j<0 or y+j>=T_num_rect[1]:
                            pass
                        elif world_backup[x+i][y+j]:
                            T_sround+=1
                if world_backup[x][y]:#生存法则
                    if T_sround<=T_live[1] and T_sround>=T_live[0]:
                        world[x][y][0]=True
                    else:
                        world[x][y][0]=False
                else:#诞生法则
                    if T_sround<=T_birth[1] and T_sround>=T_birth[0]:
                        world[x][y][0]=True
                    else:
                        world[x][y][0]=False
        #计时器重置
        time=0
    console_buttons.append(console_button('下一帧', (console_Surface_width*3/4,line),True,function=f))
    line+=console_font_size*2.5
    console_font_size*=2
    def f():
        nonlocal pause
        pause=not pause
        #时停按钮————console_button_time
    console_button_time=console_button('正在运行' if not pause else '砸瓦鲁多', (console_Surface_width/2,line),True,1.1,function=f)
    console_buttons.append(console_button_time) 
    line+=console_font_size
    console_font_size//=2
    line+=console_font_size
        #更新间隔帧数显示按钮————console_button_fps
    console_button_fps=console_button('更新间隔帧数:%d'%(T_update_time),(console_Surface_width/2,line))
    console_buttons.append(console_button_fps)
    def f():
        nonlocal console_button_fps
        global T_update_time
        if T_update_time>1:
            T_update_time-=1
        console_button_fps.text='更新间隔帧数:%d'%(T_update_time)
    console_buttons.append(console_button('<', (console_Surface_width/20,line),True,function=f))
    def f():
        nonlocal console_button_fps
        global T_update_time
        T_update_time+=1
        console_button_fps.text='更新间隔帧数:%d'%(T_update_time)
    console_buttons.append(console_button('>', (console_Surface_width*19/20,line),True,function=f))
    line+=console_font_size*3
    console_font_size*=1.5
    block_file_list=os.listdir('blocks/')
    block_list=['保存为块','删除元胞']#block_list[0]是添加块按键,block_list[1]是删除快捷键
    block_list.extend([os.path.splitext(i)[0] for i in block_file_list])
    block_list_pointer=0
    console_buttons.append(console_button('Block', (console_Surface_width/2,line)))
    def f():
        nonlocal block_list_pointer,console_button_blockname
        block_list_pointer-=1
        if block_list_pointer<0:
            block_list_pointer%=len(block_list)
        console_button_blockname.text=block_list[block_list_pointer]
    console_buttons.append(console_button('<', (console_Surface_width/8,line),True,function=f))
    def f():
        nonlocal block_list_pointer,console_button_blockname
        block_list_pointer+=1
        lenth=len(block_list)
        if block_list_pointer>=lenth:
            block_list_pointer%=lenth
        console_button_blockname.text=block_list[block_list_pointer]
    console_buttons.append(console_button('>', (console_Surface_width*7/8,line),True,function=f))
    line+=console_font_size
    #定义块预览窗口
    block_Surface_rect_width=console_Surface_width*9//10
    line+=block_Surface_rect_width//2
    block_Surface=pygame.Surface((block_Surface_rect_width,block_Surface_rect_width))
    block_Surface_rect=block_Surface.get_rect()
    block_Surface_rect.center=(console_Surface_width//2,line)
    block_function_list=[]#block图标绘制————[0]保存为块图标,[1]删除元胞图标,[2]显示预览
    block_0_image=pygame.Surface((block_Surface_rect_width,block_Surface_rect_width)).convert()
    pygame.draw.circle(block_0_image,(255,255,255),(block_Surface_rect_width//2,block_Surface_rect_width//2),block_Surface_rect_width*5//12,block_Surface_rect_width//40)
    pygame.draw.line(block_0_image,(255,255,255),(block_Surface_rect_width//4,block_Surface_rect_width//2),(block_Surface_rect_width*3//4,block_Surface_rect_width//2),block_Surface_rect_width//10)
    pygame.draw.line(block_0_image,(255,255,255),(block_Surface_rect_width//2,block_Surface_rect_width//4),(block_Surface_rect_width//2,block_Surface_rect_width*3//4),block_Surface_rect_width//10)
    block=[]#block[y][x]
    def f():
        block_Surface.blit(block_0_image,(0,0,block_Surface_rect_width,block_Surface_rect_width))
    block_function_list.append(f)
    def f():
        block_1_image=pygame.transform.rotate(block_0_image,45)
        rect=block_1_image.get_rect()
        rect.center=block_Surface_rect_width//2,block_Surface_rect_width//2
        block_Surface.blit(block_1_image,rect)
    block_function_list.append(f)
    def f():
        nonlocal block#block[y][x]
        block=[]
        with open('blocks/%s'%block_file_list[block_list_pointer-2],'rt',encoding='utf-8') as block_file:
            for line in block_file:
                block_line=[]
                block.append(block_line)
                for T in line:
                    if T=='〇':
                        block_line.append(False)
                    elif T=='壹':
                        block_line.append(True)
        num_rect=[len(block[0]),len(block)]
        num_lenth=num_rect[0] if num_rect[0]>num_rect[1] else num_rect[1]
        if num_lenth*(T_room+T_size)>=block_Surface_rect_width*9//10:
            T_size_now=(block_Surface_rect_width*9/10)//num_lenth-T_room
        else:
            T_size_now=T_size
        block_image=pygame.Surface((num_rect[0]*(T_room+T_size_now),num_rect[1]*(T_room+T_size_now)))
        for x in range(num_rect[0]):
            for y in range(num_rect[1]):
                if block[y][x]:
                    pygame.draw.rect(block_image,(255,255,255),(T_room+(T_room+T_size_now)*x,T_room+(T_room+T_size_now)*y,T_size_now,T_size_now),0)
        block_image_rect=block_image.get_rect()
        block_image_rect.center=block_Surface_rect_width//2,block_Surface_rect_width//2
        block_Surface.blit(block_image,block_image_rect)
    block_function_list.append(f)
    line+=block_Surface_rect_width//2
    console_font_size=console_font_size_backup
        #blockname显示按钮————console_button_blockname
    line+=console_font_size
    console_button_blockname=console_button(block_list[block_list_pointer], (console_Surface_width//2,line))
    console_buttons.append(console_button_blockname)
    #继续按键定义
    line+=console_font_size*2.5
        #歌曲控制按钮————console_button_music
    console_button_music_text_list='正在播放','播放控制器'
    music_play=True
    def f():
        nonlocal music_play,console_button_music
        if music_play:
            music_play=False
            console_button_music.text=console_button_music_text_list[1]
        else :
            music_play=True
            console_button_music.text=console_button_music_text_list[0]
    console_button_music=console_button(console_button_music_text_list[0], (console_Surface_width/2,line),True,1.1,function=f)
    console_buttons.append(console_button_music)
    console_font_size*=1.5
    #音乐播放
    music_list_pointer=0
    music_list_pointer_backup=music_list_pointer
    music_file_list=os.listdir('musics/')
    music_list=[os.path.splitext(i)[0] for i in music_file_list]
    music_player.load('musics/%s'%music_file_list[music_list_pointer])
    def f():
        nonlocal music_list_pointer,console_button_musicname
        music_list_pointer-=1
        if music_list_pointer<=0:
            music_list_pointer%=len(music_list)
    console_buttons.append(console_button('<', (console_Surface_width/7,line),True,function=f))
    def f():
        nonlocal music_list_pointer,console_button_musicname
        lenth=len(music_list)
        music_list_pointer+=1
        if music_list_pointer>=lenth:
            music_list_pointer%=lenth
    console_buttons.append(console_button('>', (console_Surface_width*6/7,line),True,function=f))
    console_font_size=console_font_size_backup
        #歌曲显示按钮————console_button_musicname
    line+=console_font_size*1.5
    console_button_musicname=console_button(music_list[music_list_pointer], (console_Surface_width/2,line))
    console_buttons.append(console_button_musicname)
    line=screen_info.current_h-console_font_size*2
    def f():
        window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//5))
        window_rect=window.get_rect()
        window_rect.center=screen_info.current_w//2,screen_info.current_h//2
        file_name=''#文件名（不含后缀）
        class Button(console_button):
            def draw(self):
                image=self.images[1] if self.bigger else self.images[0]
                rect=image.get_rect()
                rect.center=self.center
                window.blit(image,rect)
        button_list=[Button('另存为', (window_rect.width//2,window_rect.height//4)),\
                     Button('%s|'%file_name, (window_rect.width//2,window_rect.height//2)),\
                     Button('确定',(window_rect.width//4,window_rect.height*3//4),True),\
                     Button('取消',(window_rect.width*3//4,window_rect.height*3//4),True)]
        while True:
            for button in button_list:
                button.bigger=False
            mouse_button_cache=[False,None]
            cache_down=False#鼠标是否按下按钮
            key_down=False
            yes=False
            selected=False
            while True:
                for event in pygame.event.get():
                    if event.type==2:#keydown
                        if event.key==8:#退格键
                            index=len(file_name)-1
                            if not index<0:
                                file_name=file_name[:index]
                                button_list[1].text='%s|'%file_name
                        elif event.key==13:#回车
                            key_down=True
                            button_list[2].bigger=True
                            yes=True
                        else:
                            file_name='%s%s'%(file_name,event.unicode)
                            button_list[1].text='%s|'%file_name
                    elif event.type==3:#keyup
                        if event.key==13:
                            selected=True
                    elif event.type==4:#mouse_move
                        if not key_down:
                            mouse_button_cache=[False,None]
                            for button in button_list:
                                if button.is_button:
                                    button_rect=button.images[1 if button.bigger else 0].get_rect()
                                    if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                        mouse_button_cache=[True,button]
                                        if not cache_down:
                                            button.bigger=True
                                    else:
                                        button.bigger=False
                    elif event.type==5:#mouse_down
                        if mouse_button_cache[0] and not key_down:
                            mouse_button_cache[1].bigger=False
                            cache_down=True
                    elif event.type==6:#mouse_up
                        cache_down=False
                        if mouse_button_cache[0] and not key_down:
                            mouse_button_cache[1].bigger=True
                            selected=True
                            if button_list.index(mouse_button_cache[1])==2:
                                yes=True
                            else:
                                yes=False
                    elif event.type==12:#QUIT
                        sys.exit(0)
                #显示
                window.fill((0,0,0))
                pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                for button in button_list:
                    button.draw()
                screen.blit(window,window_rect)
                pygame.display.flip()
                if selected:
                    break
            #开始保存
            def save():#储存，成功则返回True，失败返回False
                file_full_name='%s.txt'%file_name
                file_list=os.listdir('saves/')
                if file_full_name in file_list:#存在同名文件
                    yes=False
                    selected=False
                    mouse_button_cache=[False,None]
                    mouse_down=False
                    class Button(console_button):
                        def draw(self):
                            image=self.images[1] if self.bigger else self.images[0]
                            rect=image.get_rect()
                            rect.center=self.center
                            window.blit(image,rect)
                    window=pygame.Surface((screen_info.current_w//2,screen_info.current_w//6))
                    window.fill((0,0,0))
                    window_rect=window.get_rect()
                    window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                    button_list=[Button('是否覆盖同名存档？', (window_rect.width//2,window_rect.height//3)),\
                                 Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                 Button('否[N]',(window_rect.width*3//4,window_rect.height*2//3),True)]
                    while True:#覆盖询问窗口
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                pass
                            elif event.type==3:#keyup
                                if event.key==121:#y
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                                    yes=True
                                    selected=True
                                else:
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                    selected=True
                            elif event.type==4:#mouse_move
                                mouse_button_cache=[False,None]
                                for button in button_list:
                                    if button.is_button:
                                        if button.bigger:
                                            button_rect=button.images[1].get_rect()
                                        else:
                                            button_rect=button.images[0].get_rect()
                                        button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                        if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                            mouse_button_cache[0]=True
                                            mouse_button_cache[1]=button
                                            if not mouse_down:
                                                mouse_button_cache[1].bigger=True
                                        else:
                                            button.bigger=False
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=False
                                else :
                                    for button in button_list[1:]:
                                        button.bigger=False
                                mouse_down=True
                            elif event.type==6:#mouse_up
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==1:
                                        yes=True
                                mouse_down=False
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        if selected:
                            break
                    if not yes:return False
                #开始存档
                try:
                    with open('saves/%s'%file_full_name,mode="wt",encoding="utf-8") as file:
                        file.write('<Ts>\n')
                        for y in range(T_num_rect[1]):
                            for x in range(T_num_rect[0]):
                                if world[x][y][0]:
                                    file.write('壹')
                                else:
                                    file.write('〇')
                            file.write('\n')
                        file.write('<Settings>\n')
                        file.writelines(['%s\n'%i for i in\
                                        ['T_size=%d'%T_size,\
                                         'T_room=%d'%T_room,\
                                         'T_radius=%d'%T_radius,\
                                         'T_birth=%s'%str(T_birth),\
                                         'T_live=%s'%str(T_live),\
                                         'world_history_max_len=%d'%world_history_max_len,\
                                         'display_history=%d'%int(display_history),\
                                         'history_color1=%s'%str(history_color1),\
                                         'display_history_depth=%d'%display_history_depth,\
                                         'display_history_kind=%d'%int(display_history_kind),\
                                         'display_T_Surface_side=%d'%int(display_T_Surface_side),\
                                         'advance_pause=%d'%int(advance_pause),\
                                         'ghost_color=%s'%str(ghost_color),\
                                         ]])
                except:
                    def error_window():
                        yes=False
                        key_cache=False
                        mouse_cache=False
                        class Button(console_button):
                            def draw(self):
                                image=self.images[1] if self.bigger else self.images[0]
                                rect=image.get_rect()
                                rect.center=self.center
                                window.blit(image,rect)
                        window=pygame.Surface((screen_info.current_w*3//8,screen_info.current_w//6))
                        window_rect=window.get_rect()
                        window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                        button_list=[Button('存档创建失败', (window_rect.width//2,window_rect.height//4)),\
                                     Button('请不要使用非法字符创建存档', (window_rect.width//2,window_rect.height//2)),\
                                     Button('[知道了]', (window_rect.width//2,window_rect.height*3//4),True)]
                        while True:#文件创建失败提示窗口
                            for event in pygame.event.get():
                                if event.type==2:
                                    button_list[2].bigger=True
                                    key_cache=True
                                elif event.type==3:
                                    button_list[2].bigger=False
                                    key_cache=False
                                    yes=True
                                elif event.type==4:
                                    if not (key_cache and mouse_cache):
                                        button=button_list[2]
                                        button_rect=button.images[1 if button.bigger else 0].get_rect()
                                        if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                            button.bigger=True
                                        else:
                                            button.bigger=False
                                elif event.type==5:
                                    if not key_cache:
                                        if button_list[2].bigger:
                                            button_list[2].bigger=False
                                            mouse_cache=True
                                elif event.type==6:
                                    if mouse_cache:
                                        button_list[2].bigger=True
                                        yes=True
                                elif event.type==12:
                                    sys.exit(0)
                            window.fill((0,0,0))
                            pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                            for button in button_list:
                                button.draw()
                            screen.blit(window,window_rect)
                            pygame.display.flip()
                            if yes:
                                return
                    error_window()
                    return False
                return True
            if yes:
                if save():
                    break
            else:
                break
    '''哼哼，啊啊啊啊啊啊啊啊啊啊啊啊，啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊'''
    console_buttons.append(console_button('保存', (console_Surface_width/4,line),True,function=f))
    def f():
        nonlocal _exit
        class Button(console_button):
            def draw(self):
                image=self.images[1] if self.bigger else self.images[0]
                rect=image.get_rect()
                rect.center=self.center
                window.blit(image,rect)
        yes=False
        window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//6))
        window_rect=window.get_rect()
        pygame.draw.rect(window,(255,255,255),window_rect,6)
        window_rect.center=screen.get_rect().center
        button_list=[Button('确定要退出吗？',(window_rect.width//2,window_rect.height//3),False),\
                     Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                     Button('否[N]', (window_rect.width*3//4,window_rect.height*2//3),True)]
        for button in button_list[1:]:
            button.bigger=True
        mouse_button_cache=[False,None]
        while True:#退出询问事件
            window.fill((0,0,0))
            pygame.draw.rect(window,(255,255,255),(0,0,window_rect[2],window_rect[3]),6)
            selected=False
            for event in pygame.event.get():
                if event.type==2:#keydown
                    if event.key==121:#y
                        button_list[1].bigger=False
                        button_list[2].bigger=True
                    else:
                        button_list[1].bigger=True
                        button_list[2].bigger=False
                elif event.type==3:#keyup
                    if event.key==121:#y
                        button_list[1].bigger=True
                        button_list[2].bigger=False
                        yes=True
                        selected=True
                    else:
                        button_list[1].bigger=False
                        button_list[2].bigger=True
                        selected=True
                elif event.type==4:#mouse_move
                    mouse_button_cache=[False,None]
                    for button in button_list:
                        if button.is_button:
                            if button.bigger:
                                button_rect=button.images[1].get_rect()
                            else:
                                button_rect=button.images[0].get_rect()
                            button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                            if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                mouse_button_cache[0]=True
                                mouse_button_cache[1]=button
                            else:
                                button.bigger=True
                elif event.type==5:#mouse_down
                    if mouse_button_cache[0]:
                        mouse_button_cache[1].bigger=False
                    else :
                        for button in button_list[1:]:
                            button.bigger=True
                elif event.type==6:#mouse_up
                    if mouse_button_cache[0]:
                        mouse_button_cache[1].bigger=True
                        selected=True
                        if button_list.index(mouse_button_cache[1])==1:
                            yes=True
                elif event.type==12:#QUIT
                    sys.exit(0)
            for button in button_list:
                button.draw()
            screen.blit(window,window_rect)
            pygame.display.flip()
            if selected:
                break
        if yes:
            _exit=True
        return
    console_buttons.append(console_button('退出', (console_Surface_width*3/4,line),True,function=f))
    
    #元胞世界定义
    T_Surface_bigrect=((console_Surface_width,0),(screen_info.current_w-console_Surface_width,screen_info.current_h))
    T_num_rect=(T_Surface_bigrect[1][0]//(T_size+T_room),T_Surface_bigrect[1][1]//(T_size+T_room))
    T_Surface_room=(T_Surface_bigrect[1][0]%(T_size+T_room),T_Surface_bigrect[1][1]%(T_size+T_room))
    T_Surface_rect=((T_Surface_room[0]//2+console_Surface_width,T_Surface_room[1]//2) , (T_num_rect[0]*(T_room+T_size),T_num_rect[1]*(T_room+T_size)) )
    #要求：输出元胞的时候先输出空隙
    T_Surface=pygame.Surface(T_Surface_rect[1])#元胞画布
    #T_Surface_rect[0]是绘制元胞画布的起始点
    world=[[[False,T_room+i*(T_room+T_size),T_room+j*(T_room+T_size)] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])]
    for y in range(len(world_save)):
        for x in range(len(world_save[0])):
            try:
                world[x][y][0]=False if world_save[y][x]=='〇' else True
            except IndexError:
                pass
    #world[x_num][y_num][0——状态，1——x位置，2——y位置]
    world_backup_list=[]#用来堆叠历史状态
    world_mouse_down_up_tuple=[False,False,[0,0],[0,0],False]#[0]是否按下,[1]是否抬起(GO!)，[2]终点坐标，[3]起点坐标，[4]是否处于元胞画布
    
    while True:
        
        #音乐播放
        if music_list_pointer != music_list_pointer_backup:#老板换碟！
            music_list_pointer_backup=music_list_pointer
            music_player.load('musics/%s'%music_file_list[music_list_pointer])
            console_button_musicname.text=music_list[music_list_pointer]
        if music_play:
            if not music_player.get_busy():
                music_player.play()
            else:
                music_player.unpause()
        else:
            music_player.pause()
        
        #显示
        screen.fill((0,0,0))
        #控制台显示
        for button in console_buttons:
            button.draw()
        #block预览显示
        block_Surface.fill((0,0,0))
        if block_list_pointer<2:
            block_function_list[block_list_pointer]()
        else:
            block_function_list[2]()
        pygame.draw.rect(block_Surface,(255,255,255),((0,0),(block_Surface_rect_width,block_Surface_rect_width)),1)
        screen.blit(block_Surface,block_Surface_rect)
        #元胞画布显示
        if display_T_Surface_side:pygame.draw.polygon(screen,(255,255,255),((T_Surface_rect[0][0]-1,0),(T_Surface_rect[0][0]-1,screen_info.current_h)),1)
        T_Surface.fill((0,0,0))
        if display_history:#残影显示
            history_len=len(world_backup_list)
            for i in range(display_history_depth):
                world_backup_list_index=history_len-display_history_depth+i
                if world_backup_list_index<0:
                    continue
                else:
                    for x in range(T_num_rect[0]):
                        for y in range(T_num_rect[1]):
                            if world_backup_list[world_backup_list_index][x][y]:
                                pygame.draw.rect(T_Surface, history_colors[i], ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
        if world_mouse_down_up_tuple[4]:#鬼影显示
            if block_list_pointer==0:#保存为块
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        pygame.draw.rect(T_Surface,ghost_color, ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
            elif block_list_pointer==1:#删除元胞
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        pygame.draw.rect(T_Surface,ghost_color, ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
            else:#写入块
                def f(x0,xt,y0,yt):#象限判断
                    if xt>=x0 and yt>=y0:
                        return 4
                    elif xt>=x0 and yt<y0:
                        return 1
                    elif xt<x0 and yt<y0:
                        return 2
                    else:
                        return 3
                angle=f(world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                block_rect=len(block[0]),len(block)
                if angle==1:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+y,world_mouse_down_up_tuple[3][1]-x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==2:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-x,world_mouse_down_up_tuple[3][1]-y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==3:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-y,world_mouse_down_up_tuple[3][1]+x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
                elif angle==4:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+x,world_mouse_down_up_tuple[3][1]+y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    T=world[pos[0]][pos[1]]
                                    pygame.draw.rect(T_Surface, ghost_color, ((T[1],T[2]),(T_size,T_size)),0)
        for x in range(T_num_rect[0]):#元胞显示
            for y in range(T_num_rect[1]):
                if world[x][y][0]:
                    pygame.draw.rect(T_Surface,(255,255,255), ((world[x][y][1],world[x][y][2]),(T_size,T_size)),0)
        screen.blit(T_Surface,T_Surface_rect[0])
        #最终显示
        pygame.display.flip()
        
        mouse_once_up=False
        for event in pygame.event.get():#事件处理
            if event.type==1:#application_event
                pass
            elif event.type==2:#keydown
                if event.key==27:#ESC
                    ESC_Onece=True#是第一次按下ESC键
                    class Button(console_button):
                        def draw(self):
                            image=self.images[1] if self.bigger else self.images[0]
                            rect=image.get_rect()
                            rect.center=self.center
                            window.blit(image,rect)
                    yes=False
                    window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//6))
                    window_rect=window.get_rect()
                    pygame.draw.rect(window,(255,255,255),window_rect,6)
                    window_rect.center=screen.get_rect().center
                    button_list=[Button('确定要退出吗？',(window_rect.width//2,window_rect.height//3),False),\
                                 Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                 Button('否[N]', (window_rect.width*3//4,window_rect.height*2//3),True)]
                    for button in button_list[1:]:
                            button.bigger=True
                    mouse_button_cache=[False,None]
                    while True:#退出询问事件
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect[2],window_rect[3]),6)
                        selected=False
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                if event.key==121:#y
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                else:
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                            elif event.type==3:#keyup
                                if event.key==121:#y
                                    button_list[1].bigger=True
                                    button_list[2].bigger=False
                                    yes=True
                                    selected=True
                                elif event.key==27:#esc
                                    if ESC_Onece:#取消第一次的esc抬起判断
                                        ESC_Onece=False
                                    else:
                                        button_list[1].bigger=False
                                        button_list[2].bigger=True
                                        selected=True
                                else:
                                    button_list[1].bigger=False
                                    button_list[2].bigger=True
                                    selected=True
                            elif event.type==4:#mouse_move
                                mouse_button_cache=[False,None]
                                for button in button_list:
                                    if button.is_button:
                                        if button.bigger:
                                            button_rect=button.images[1].get_rect()
                                        else:
                                            button_rect=button.images[0].get_rect()
                                        button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                        if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                            mouse_button_cache[0]=True
                                            mouse_button_cache[1]=button
                                        else:button.bigger=True
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=False
                                else :
                                    for button in button_list[1:]:
                                        button.bigger=True
                            elif event.type==6:#mouse_up
                                if mouse_button_cache[0]:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==1:
                                        yes=True
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        if selected:
                            break
                    if yes:
                        _exit=True
                elif event.key==32:#Space
                    pause=not pause
            elif event.type==3:#keyup
                pass
            elif event.type==4:#mouse_move
                mouse_button_cache=[False,None]#用于判断鼠标是否被按键捕捉,捕捉的哪个键
                if event.pos[0]<=console_Surface_width:#鼠标处于控制台时
                    world_mouse_down_up_tuple[4]=False
                    for button in console_buttons:
                        if button.is_button:#如果是个按钮
                            if not button.bigger:
                                rect=button.images[0].get_rect()
                                rect.center=button.center
                                if rect.left<=event.pos[0] and rect.right>=event.pos[0] and rect.top<=event.pos[1] and rect.bottom>=event.pos[1]:
                                    button.bigger=True
                                    mouse_button_cache[0]=True
                                    mouse_button_cache[1]=button
                                else:
                                    button.bigger=False
                            else:
                                rect=button.images[1].get_rect()
                                rect.center=button.center
                                if not (rect.left<=event.pos[0] and rect.right>=event.pos[0] and rect.top<=event.pos[1] and rect.bottom>=event.pos[1]):
                                    button.bigger=False
                                else:
                                    button.bigger=True
                                    mouse_button_cache[0]=True
                                    mouse_button_cache[1]=button
                else:#鼠标处于元胞世界时
                    for button in console_buttons:#控制台按钮大小矫正
                        button.bigger=False
                    world_mouse_down_up_tuple[4]=True
                    for x in range(T_num_rect[0]+1):
                        if x==T_num_rect[0]:
                            world_mouse_down_up_tuple[2][0]=x-1
                        elif T_Surface_rect[0][0]+world[x][0][1]>event.pos[0]:
                            world_mouse_down_up_tuple[2][0]=x-1 if x>0 else 0
                            break
                    for y in range(T_num_rect[1]+1):
                        if y==T_num_rect[1]:
                            world_mouse_down_up_tuple[2][1]=y-1
                        elif T_Surface_rect[0][1]+world[0][y][2]>event.pos[1]:
                            world_mouse_down_up_tuple[2][1]=y-1 if y>0 else 0
                            break
                    if (not world_mouse_down_up_tuple[0]) and (not mouse_once_up):#如果鼠标没有按下
                        world_mouse_down_up_tuple[3]=world_mouse_down_up_tuple[2][:]
            elif event.type==5:#mouse_down
                if mouse_button_cache[0]:
                    mouse_button_cache[1].bigger=False
                else:#鼠标处于元胞世界时
                    world_mouse_down_up_tuple[4]=True
                    world_mouse_down_up_tuple[0]=True
                    world_mouse_down_up_tuple[1]=False
            elif event.type==6:#mouse_up
                if mouse_button_cache[0]:
                    mouse_button_cache[1].bigger=True
                    mouse_button_cache[1].function()
                else:#鼠标处于元胞世界时
                    world_mouse_down_up_tuple[4]=True
                    world_mouse_down_up_tuple[0]=False
                    world_mouse_down_up_tuple[1]=True
                    mouse_once_up=True
            elif event.type==12:#QUIT
                sys.exit(0)
            elif event.type==25:#音乐播放完毕
                music_list_pointer+=1
                lenth=len(music_list)
                if music_list_pointer>=lenth:
                    music_list_pointer%=lenth
        
        #元胞状态更新
        if time>=T_update_time:
            #备份
            world_backup=numpy.array([[world[i][j][0] for j in range(T_num_rect[1])] for i in range(T_num_rect[0])],dtype=bool)
            world_backup_list.append(world_backup)
            if len(world_backup_list)>world_history_max_len:
                del(world_backup_list[0])
            #(利用备份)演算新状态
            for x in range(T_num_rect[0]):
                for y in range(T_num_rect[1]):
                    T_sround=0
                    #检测周边元胞数
                    for i in range(-T_radius,T_radius+1):
                        for j in range(-T_radius,T_radius+1):
                            if (i==0 and j==0) or x+i<0 or x+i>=T_num_rect[0] or y+j<0 or y+j>=T_num_rect[1]:
                                pass
                            elif world_backup[x+i][y+j]:
                                T_sround+=1
                    if world_backup[x][y]:#生存法则
                        if T_sround<=T_live[1] and T_sround>=T_live[0]:
                            world[x][y][0]=True
                        else:
                            world[x][y][0]=False
                    else:#诞生法则
                        if T_sround<=T_birth[1] and T_sround>=T_birth[0]:
                            world[x][y][0]=True
                        else:
                            world[x][y][0]=False
            #计时器重置
            time=0

        if world_mouse_down_up_tuple[1] and world_mouse_down_up_tuple[4]:#鬼影实现
            if block_list_pointer==0:#保存为块
                #保存窗口
                window=pygame.Surface((screen_info.current_w//3,screen_info.current_w//5))
                window_rect=window.get_rect()
                window_rect.center=screen_info.current_w//2,screen_info.current_h//2
                file_name=''#文件名（不含后缀）
                class Button(console_button):
                    def draw(self):
                        image=self.images[1] if self.bigger else self.images[0]
                        rect=image.get_rect()
                        rect.center=self.center
                        window.blit(image,rect)
                button_list=[Button('Block另存为', (window_rect.width//2,window_rect.height//4)),\
                             Button('%s|'%file_name, (window_rect.width//2,window_rect.height//2)),\
                             Button('确定',(window_rect.width//4,window_rect.height*3//4),True),\
                             Button('取消',(window_rect.width*3//4,window_rect.height*3//4),True)]
                while True:
                    for button in button_list:
                        button.bigger=False
                    mouse_button_cache=[False,None]
                    cache_down=False#鼠标是否按下按钮
                    key_down=False
                    yes=False
                    selected=False
                    while True:
                        for event in pygame.event.get():
                            if event.type==2:#keydown
                                if event.key==8:#退格键
                                    index=len(file_name)-1
                                    if not index<0:
                                        file_name=file_name[:index]
                                        button_list[1].text='%s|'%file_name
                                elif event.key==13:#回车
                                    key_down=True
                                    button_list[2].bigger=True
                                    yes=True
                                else:
                                    file_name='%s%s'%(file_name,event.unicode)
                                    button_list[1].text='%s|'%file_name
                            elif event.type==3:#keyup
                                if event.key==13:
                                    selected=True
                            elif event.type==4:#mouse_move
                                if not key_down:
                                    mouse_button_cache=[False,None]
                                    for button in button_list:
                                        if button.is_button:
                                            button_rect=button.images[1 if button.bigger else 0].get_rect()
                                            if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                                mouse_button_cache=[True,button]
                                                if not cache_down:
                                                    button.bigger=True
                                            else:
                                                button.bigger=False
                            elif event.type==5:#mouse_down
                                if mouse_button_cache[0] and not key_down:
                                    mouse_button_cache[1].bigger=False
                                    cache_down=True
                            elif event.type==6:#mouse_up
                                cache_down=False
                                if mouse_button_cache[0] and not key_down:
                                    mouse_button_cache[1].bigger=True
                                    selected=True
                                    if button_list.index(mouse_button_cache[1])==2:
                                        yes=True
                                    else:
                                        yes=False
                            elif event.type==12:#QUIT
                                sys.exit(0)
                        #显示
                        window.fill((0,0,0))
                        pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                        for button in button_list:
                            button.draw()
                        screen.blit(window,window_rect)
                        pygame.display.flip()
                        if selected:
                            break
                    #开始保存
                    def save():#储存，成功则返回True，失败返回False
                        file_full_name='%s.txt'%file_name
                        file_list=os.listdir('blocks/')
                        if file_full_name in file_list:#存在同名文件
                            yes=False
                            selected=False
                            mouse_button_cache=[False,None]
                            mouse_down=False
                            class Button(console_button):
                                def draw(self):
                                    image=self.images[1] if self.bigger else self.images[0]
                                    rect=image.get_rect()
                                    rect.center=self.center
                                    window.blit(image,rect)
                            window=pygame.Surface((screen_info.current_w//2,screen_info.current_w//6))
                            window.fill((0,0,0))
                            window_rect=window.get_rect()
                            window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                            button_list=[Button('是否覆盖同名存档？', (window_rect.width//2,window_rect.height//3)),\
                                         Button('是[y]', (window_rect.width//4,window_rect.height*2//3),True),\
                                         Button('否[N]',(window_rect.width*3//4,window_rect.height*2//3),True)]
                            while True:#覆盖询问窗口
                                window.fill((0,0,0))
                                pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                                for button in button_list:
                                    button.draw()
                                screen.blit(window,window_rect)
                                pygame.display.flip()
                                for event in pygame.event.get():
                                    if event.type==2:#keydown
                                        pass
                                    elif event.type==3:#keyup
                                        if event.key==121:#y
                                            button_list[1].bigger=True
                                            button_list[2].bigger=False
                                            yes=True
                                            selected=True
                                        else:
                                            button_list[1].bigger=False
                                            button_list[2].bigger=True
                                            selected=True
                                    elif event.type==4:#mouse_move
                                        mouse_button_cache=[False,None]
                                        for button in button_list:
                                            if button.is_button:
                                                if button.bigger:
                                                    button_rect=button.images[1].get_rect()
                                                else:
                                                    button_rect=button.images[0].get_rect()
                                                button_rect.center=[button.center[i]+window_rect[i] for i in range(2)]
                                                if button_rect.left<=event.pos[0] and button_rect.right>=event.pos[0] and button_rect.top<=event.pos[1] and button_rect.bottom>=event.pos[1]:
                                                    mouse_button_cache[0]=True
                                                    mouse_button_cache[1]=button
                                                    if not mouse_down:
                                                        mouse_button_cache[1].bigger=True
                                                else:
                                                    button.bigger=False
                                    elif event.type==5:#mouse_down
                                        if mouse_button_cache[0]:
                                            mouse_button_cache[1].bigger=False
                                        else :
                                            for button in button_list[1:]:
                                                button.bigger=False
                                        mouse_down=True
                                    elif event.type==6:#mouse_up
                                        if mouse_button_cache[0]:
                                            mouse_button_cache[1].bigger=True
                                            selected=True
                                            if button_list.index(mouse_button_cache[1])==1:
                                                yes=True
                                        mouse_down=False
                                    elif event.type==12:#QUIT
                                        sys.exit(0)
                                if selected:
                                    break
                            if not yes:return False
                        #开始存档
                        try:
                            with open('blocks/%s'%file_full_name,mode="wt",encoding="utf-8") as file:
                                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                                buff=[]
                                for y in range(y0,yt+1):
                                    line=[]
                                    buff.append(line)
                                    for x in range(x0,xt+1):
                                        if world[x][y][0]:
                                            line.append('壹')
                                        else:
                                            line.append('〇')
                                #buff裁剪
                                delete_line_index=[0,0]#[0][1]表示上下实体数
                                for  i in range(len(buff)):
                                    if '壹' in buff[i]:
                                        delete_line_index[0]=i
                                        break
                                for i in reversed(range(len(buff))):
                                    if '壹' in buff[i]:
                                        delete_line_index[1]=i
                                        break
                                buff=buff[delete_line_index[0]:delete_line_index[1]+1]
                                while True:
                                    stop=False
                                    for line in buff:
                                        try:
                                            if line[0]=='壹':
                                                stop=True
                                        except IndexError:
                                            stop=True
                                    if stop:
                                        break
                                    else:
                                        for line in buff:
                                            del line[0]
                                while True:
                                    stop=False
                                    for line in buff:
                                        try:
                                            if line[-1]=='壹':
                                                stop=True
                                        except IndexError:
                                            stop=True
                                    if stop:
                                        break
                                    else:
                                        for line in buff:
                                            line.pop()
                                for line in buff:
                                    for char in line:
                                        file.write(char)
                                    file.write('\n')
                        except:
                            def error_window():
                                yes=False
                                key_cache=False
                                mouse_cache=False
                                class Button(console_button):
                                    def draw(self):
                                        image=self.images[1] if self.bigger else self.images[0]
                                        rect=image.get_rect()
                                        rect.center=self.center
                                        window.blit(image,rect)
                                window=pygame.Surface((screen_info.current_w*3//8,screen_info.current_w//6))
                                window_rect=window.get_rect()
                                window_rect.center=(screen_info.current_w//2,screen_info.current_h//2)
                                button_list=[Button('Block创建失败', (window_rect.width//2,window_rect.height//4)),\
                                             Button('请不要使用非法字符创建Block', (window_rect.width//2,window_rect.height//2)),\
                                             Button('[知道了]', (window_rect.width//2,window_rect.height*3//4),True)]
                                while True:#文件创建失败提示窗口
                                    for event in pygame.event.get():
                                        if event.type==2:
                                            button_list[2].bigger=True
                                            key_cache=True
                                        elif event.type==3:
                                            button_list[2].bigger=False
                                            key_cache=False
                                            yes=True
                                        elif event.type==4:
                                            if not (key_cache and mouse_cache):
                                                button=button_list[2]
                                                button_rect=button.images[1 if button.bigger else 0].get_rect()
                                                if window_rect.left+button.center[0]-button_rect.width//2<=event.pos[0] and window_rect.left+button.center[0]+button_rect.width//2>=event.pos[0] and window_rect.top+button.center[1]-button_rect.height//2<=event.pos[1] and window_rect.top+button.center[1]+button_rect.height//2>=event.pos[1]:
                                                    button.bigger=True
                                                else:
                                                    button.bigger=False
                                        elif event.type==5:
                                            if not key_cache:
                                                if button_list[2].bigger:
                                                    button_list[2].bigger=False
                                                    mouse_cache=True
                                        elif event.type==6:
                                            if mouse_cache:
                                                button_list[2].bigger=True
                                                yes=True
                                        elif event.type==12:
                                            sys.exit(0)
                                    window.fill((0,0,0))
                                    pygame.draw.rect(window,(255,255,255),(0,0,window_rect.width,window_rect.height),6)
                                    for button in button_list:
                                        button.draw()
                                    screen.blit(window,window_rect)
                                    pygame.display.flip()
                                    if yes:
                                        return
                            error_window()
                            return False
                        return True
                    if yes:
                        if save():
                            break
                    else:
                        break
                #列表更新
                block_file_list=os.listdir('blocks/')
                block_list=['保存为块','删除元胞']
                block_list.extend([os.path.splitext(i)[0] for i in block_file_list])
            elif block_list_pointer==1:#删除元胞
                (x0,xt)=(world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][0]) if world_mouse_down_up_tuple[2][0]<=world_mouse_down_up_tuple[3][0] else (world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0])
                (y0,yt)=(world_mouse_down_up_tuple[2][1],world_mouse_down_up_tuple[3][1]) if world_mouse_down_up_tuple[2][1]<=world_mouse_down_up_tuple[3][1] else (world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                for x in range(x0,xt+1):
                    for y in range(y0,yt+1):
                        world[x][y][0]=False
            else:#写入元胞
                def f(x0,xt,y0,yt):#象限判断
                    if xt>=x0 and yt>=y0:
                        return 4
                    elif xt>=x0 and yt<y0:
                        return 1
                    elif xt<x0 and yt<y0:
                        return 2
                    else:
                        return 3
                angle=f(world_mouse_down_up_tuple[3][0],world_mouse_down_up_tuple[2][0],world_mouse_down_up_tuple[3][1],world_mouse_down_up_tuple[2][1])
                block_rect=len(block[0]),len(block)
                if angle==1:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+y,world_mouse_down_up_tuple[3][1]-x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==2:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-x,world_mouse_down_up_tuple[3][1]-y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==3:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]-y,world_mouse_down_up_tuple[3][1]+x
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
                elif angle==4:
                    for x in range(block_rect[0]):
                        for y in range(block_rect[1]):
                            if block[y][x]:
                                pos=world_mouse_down_up_tuple[3][0]+x,world_mouse_down_up_tuple[3][1]+y
                                if (pos[0]>=0 and pos[0]<T_num_rect[0])and(pos[1]>=0 and pos[1]<T_num_rect[1]):
                                    world[pos[0]][pos[1]][0]=True
            #必要后缀步骤
            world_mouse_down_up_tuple[3]=world_mouse_down_up_tuple[2][:]
            world_mouse_down_up_tuple[1]=False
        if not pause:
            time+=1
            console_button_time.text='正在运行'
        else:console_button_time.text='砸瓦鲁多'
        if _exit:
            if music_player.get_busy():
                music_player.fadeout(10000)
            return
        
#设置界面
def options_UI():
    font_size=screen_info.current_w/40
    class Message_Button():
        def __init__(self,text,center,is_button=False,x=1.25,function=lambda:None):
            self.bigger=False
            self.fonts=[pygame.font.Font('font.ttf',int(i*font_size)) for i in (1,x)]
            self.text=text
            self.is_button=is_button
            self.images#跟随self.text变化，[0]和[1]分别为常规和大号
            self.image
            self.center=tuple(int(i) for i in center)
            self.function=function
        def draw(self):
            rect=self.image.get_rect()
            rect.center=self.center
            screen.blit(self.image,rect)
        def __setattr__(self, name, value):
            object.__setattr__(self,name,value)
            if name=='text':#用于文本发生变化时的图像自动更新
                self.images=[font.render(value, True, (255,255,255)) for font in self.fonts]
        def __getattribute__(self,name):
            if name=='image':
                return self.images[1 if self.bigger else 0]
            else: return object.__getattribute__(self, name)
    def message(text):
        main_message=Message_Button(text,(screen_info.current_w//2,font_size*6))
        then_message=Message_Button('按任意键继续......',(screen_info.current_w//2,screen_info.current_h*2//3))
        while True:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type==12:
                    sys.exit(0)
                elif event.type==2:
                    then_message.bigger=True
                elif event.type==3:
                    return
                elif event.type==5:
                    then_message.bigger=True
                elif event.type==6:
                    return
            main_message.draw()
            then_message.draw()
            pygame.display.flip()
    message('不想写选项了::>_<::')
    message('其实我们可以通过改存档来修改设置( •̀ ω •́ )✧')
    message('存档在save目录下，修改的时候可以参照根目录下的一个对应表(~￣▽￣)~')
    message('溜了溜了ε=ε=ε=(~￣▽￣)~')

#其它界面
def other_UI():
    font_size=screen_info.current_w/40
    class Message_Button():
        def __init__(self,text,center,is_button=False,x=1.25,function=lambda:None):
            self.bigger=False
            self.fonts=[pygame.font.Font('font.ttf',int(i*font_size)) for i in (1,x)]
            self.text=text
            self.is_button=is_button
            self.images#跟随self.text变化，[0]和[1]分别为常规和大号
            self.image
            self.center=tuple(int(i) for i in center)
            self.function=function
        def draw(self):
            rect=self.image.get_rect()
            rect.center=self.center
            screen.blit(self.image,rect)
        def __setattr__(self, name, value):
            object.__setattr__(self,name,value)
            if name=='text':#用于文本发生变化时的图像自动更新
                self.images=[font.render(value, True, (255,255,255)) for font in self.fonts]
        def __getattribute__(self,name):
            if name=='image':
                return self.images[1 if self.bigger else 0]
            else: return object.__getattribute__(self, name)
    def message(text):
        main_message=Message_Button(text,(screen_info.current_w//2,font_size*6))
        then_message=Message_Button('按任意键继续......',(screen_info.current_w//2,screen_info.current_h*2//3))
        while True:
            screen.fill((0,0,0))
            for event in pygame.event.get():
                if event.type==12:
                    sys.exit(0)
                elif event.type==2:
                    then_message.bigger=True
                elif event.type==3:
                    return
                elif event.type==5:
                    then_message.bigger=True
                elif event.type==6:
                    return
            main_message.draw()
            then_message.draw()
            pygame.display.flip()
    message('才不会告诉你Space键是时停的快捷键')
    message('(⊙x⊙)')
    message('总之。。。。。。')
    message('感谢游玩本游戏~ (/ω＼*)……… (/ω•＼*)')
    surface=pygame.Surface((screen_info.current_w,screen_info.current_h))
    font=pygame.font.Font('font.ttf',int(font_size))
    image=pygame.image.load('back_ground').convert()
    image.set_alpha(50)
    image_rect=image.get_rect()
    image_rect.right,image_rect.bottom=screen_info.current_w,screen_info.current_h
    surface.blit(image,image_rect)
    font1=font.render('@author: echo', True, (255,255,255))
    font1_rect=font1.get_rect()
    font1_rect.center=screen_info.current_w//2,screen_info.current_h//5
    font2=font.render('Thu Jul  2 14:28:47 2020  ——  Sun Jul 12 20:44:40 2020', True,(255,255,255))
    font2_rect=font2.get_rect()
    font2_rect.center=screen_info.current_w//2,screen_info.current_h*3//5
    surface.blit(font1,font1_rect)
    surface.blit(font2,font2_rect)
    light=0
    while True:
        screen.fill((0,0,0))
        light+=0.01
        if light<=1:
            surface.set_alpha(255*light)
        elif light>1 and light<=2:
            surface.set_alpha(255)
        elif light>2 and light<=3:
            surface.set_alpha(255*(3-light))
        else:
            break
        screen.blit(surface,(0,0,screen_info.current_w,screen_info.current_h))
        pygame.display.flip()
    
#通过主界面选择调用不同程序
def main_select(n):
    if n==0:
        game_UI()
    elif n==1:
        read_UI()
    elif n==2:
        options_UI()
    elif n==3:
        other_UI()
    else:
        sys.exit(0)

#界面循环
while True:
    main_select(main_UI())
