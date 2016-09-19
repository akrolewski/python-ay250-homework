
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

class RectangleBuilder:
    def __init__(self, rect, data, all_axes, all_plots, fig):
        self.rect = rect
        self.data = data
        self.all_axes = all_axes
        self.all_plots = all_plots
        self.figure = fig
        self.pressed = False
        
        self.topx = None
        self.topy = None
        self.botx = None
        self.boty = None
        
    def connect(self):
        self.cidpress = self.rect.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidmotion = self.rect.figure.canvas.mpl_connect('motion_notify_event',self.expand_on_motion)
        self.cidrelease = self.rect.figure.canvas.mpl_connect('button_release_event', self.brush_on_release)
        self.cidkey = self.rect.figure.canvas.mpl_connect('key_press_event',self.unbrush_on_mouseover)
        
    def on_press(self, event):
        if event.inaxes!=self.rect.axes: return
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.pressed = True
        
    def expand_on_motion(self, event):
        if event.inaxes!=self.rect.axes: return
        if not self.pressed: return
        self.x2 = event.xdata
        self.y2 = event.ydata
        topx = max([self.x1,self.x2])
        botx = min([self.x1,self.x2])
        topy = max([self.y1,self.y2])
        boty = min([self.y1,self.y2])
        
        self.topx = topx
        self.botx = botx
        self.topy = topy
        self.boty = boty
        
        self.rect.set_visible(True)
        self.rect.set_xy((botx,boty))
        self.rect.set_width(np.abs(self.x2-self.x1))
        self.rect.set_height(np.abs(self.y2-self.y1))
        self.rect.figure.canvas.draw()
        
        
    def brush_on_release(self,event):
        if event.inaxes!=self.rect.axes: return
        self.pressed = False
        self.x2 = event.xdata
        self.y2 = event.ydata
        topx = max([self.x1,self.x2])
        botx = min([self.x1,self.x2])
        topy = max([self.y1,self.y2])
        boty = min([self.y1,self.y2])
        
        self.topx = topx
        self.botx = botx
        self.topy = topy
        self.boty = boty
        
        self.rect.set_visible(True)
        self.rect.set_xy((botx,boty))
        self.rect.set_width(np.abs(self.x2-self.x1))
        self.rect.set_height(np.abs(self.y2-self.y1))
        self.rect.figure.canvas.draw()
        
        ij = np.where(self.all_axes == self.rect.axes)
        # Assumption: all subplots have the same facecolor and edgecolor...
        datax = self.data[:,ij[0][0]]
        datay = self.data[:,ij[1][0]]
        
        brush_alpha_val = 0.3
        
        plot = self.all_plots[ij[0][0],ij[1][0]]
        fc = plot.get_facecolor()
        ec = plot.get_edgecolor()
        new_rgba_fc = np.zeros((datax.shape[0],4))
        new_rgba_fc[:,0:3] = fc[0][0:3]
        new_rgba_fc[:,3] = 1.0
        new_rgba_fc[:,3][(datax > topx) | (datax < botx) | (datay > topy) | (datay < boty)] = brush_alpha_val
        
        new_rgba_ec = np.zeros((datax.shape[0],4))
        new_rgba_ec[:,0:3] = ec[0][0:3]
        new_rgba_ec[:,3] = 1.0
        new_rgba_ec[:,3][(datax > topx) | (datax < botx) | (datay > topy) | (datay < boty)] = brush_alpha_val
        
        for plot in self.all_plots.flatten():
            plot.set_facecolors(new_rgba_fc)
            plot.set_edgecolors(new_rgba_ec)
        self.figure.canvas.draw()
        
    def unbrush_on_mouseover(self,event):
        if event.inaxes!=self.rect.axes: return
        x = event.xdata
        y = event.ydata
        if self.botx and self.topx and self.boty and self.topy and self.rect.get_visible():
            if x > self.botx and x < self.topx and y > self.boty and y < self.topy:
                if event.key == 'd':
                    ij = np.where(self.all_axes == self.rect.axes)
                    plot = self.all_plots[ij[0][0],ij[1][0]]
                    fc = plot.get_facecolor()
                    ec = plot.get_edgecolor()
                    
                    datax = self.data[:,ij[0][0]]
                    
                    new_rgba_fc = np.zeros((datax.shape[0],4))
                    new_rgba_fc[:,0:3] = fc[0][0:3]
                    new_rgba_fc[:,3] = 1.0
                    
                    new_rgba_ec = np.zeros((datax.shape[0],4))
                    new_rgba_ec[:,0:3] = ec[0][0:3]
                    new_rgba_ec[:,3] = 1.0
                    
                    for plot in self.all_plots.flatten():
                        plot.set_facecolors(new_rgba_fc)
                        plot.set_edgecolors(new_rgba_ec)
                    
                    self.rect.set_visible(False)
                    
                    self.figure.canvas.draw()
                    
            
def brushing(data):
    fig, ax_arr = plt.subplots(data.shape[1],data.shape[1],figsize=(10,10))
    all_plots = np.zeros_like(ax_arr)
    for i in range(ax_arr.shape[0]):
        for j in range(ax_arr.shape[1]):
            all_plots[i,j] = ax_arr[i,j].scatter(data[:,i],data[:,j],facecolor='b',edgecolor='b')
            if i != 3:
                plt.setp(ax_arr[i,j].get_xticklabels(),visible=False)
            if j != 0:
                plt.setp(ax_arr[i,j].get_yticklabels(),visible=False)
                
    lb = []
    for i in range(len(ax_arr.flatten())):
        ax = ax_arr.flatten()[i]
        rect = matplotlib.patches.Rectangle((0,0),0,0,facecolor='none')
        ax.add_patch(rect)
        lb.append(RectangleBuilder(rect, data, ax_arr, all_plots, fig))
        lb[i].connect()
        
    plt.show()