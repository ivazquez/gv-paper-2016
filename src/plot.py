# -*- coding: utf-8 -*-
hatches = []

import colors, utils

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib import lines,ticker
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import numpy as np

def histogram_binned_data(ax, data, bins=50):
    
    nx, xbins = np.histogram(data, bins=bins, normed=True)

    nx_frac = nx/float(len(nx)) # each bin divided by total number of objects.
    width = xbins[1] - xbins[0] # width of each bin.
    x = np.ravel(zip(xbins[:-1], xbins[:-1]+width))
    y = np.ravel(zip(nx_frac,nx_frac))
    
    return x, y

def boxplot_custom(bp, ax, colors=colors, hatches=hatches):
    for i in range(len(bp['boxes'])):
        box = bp['boxes'][i]
        box.set_linewidth(0)
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
            boxCoords = zip(boxX,boxY)
            boxPolygon = Polygon(boxCoords, 
                                 facecolor = colors[i % len(colors)], 
                                 linewidth=0, 
                                 hatch = hatches[i % len(hatches)])
            ax.add_patch(boxPolygon)

    for i in range(0, len(bp['boxes'])):
        bp['boxes'][i].set_color(colors[i])
        # bp['boxes'][i].set_hatch(' ')

        # we have two whiskers!
        bp['whiskers'][i*2].set(color=colors[i], 
                                linewidth=1.5,
                                linestyle='-')
        bp['whiskers'][i*2 + 1].set(color=colors[i], 
                                linewidth=1.5,
                                linestyle='-')
        # top and bottom fliers
        bp['fliers'][i].set(markerfacecolor=colors[i],
                            marker='o', alpha=0.75, markersize=3,
                            markeredgecolor='none')
        bp['medians'][i].set_color('black')
        bp['medians'][i].set_linewidth(2)
        # and 4 caps to remove
        for c in bp['caps']:
            c.set_linewidth(0)

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.tick_params(axis='y', length=0)

    ax.grid(axis='y', color="0.9", linestyle='-', linewidth=1)
    ax.set_axisbelow(True)
    
    
from matplotlib.collections import PatchCollection


def heatmap_spores(S, ax, title, xlabel, ylabel, xticklabels, yticklabels, fold=False, cmap='RdBu', radius=0.25):
    '''
    
    '''
    
    dict_mat = {u'MATa':{'x':[-radius]*len(S.loc[u'MATa']), 'y':np.arange(0.5,len(S.loc[u'MATa']))},
                u'MATα':{'x':np.arange(0.5,len(S.loc[u'MATα'])), 'y':[-radius]*len(S[u'MATα'])}}
    
    for mating in dict_mat.iterkeys():
        data = map(list, zip(*[dict_mat[mating]['x'], dict_mat[mating]['y']]))
        circles = [plt.Circle([x, y], radius) for (x, y) in data]
        col = PatchCollection(circles, edgecolor='black', lw=0.75)

        s = S.ix[mating].values
        
        # shift colormap
        orig_cmap = cmap
        mid = (1 - np.ma.max(S)/(np.ma.max(S) + abs(np.ma.min(S))))
                    
        shifted_cmap = utils.shift_colormap(orig_cmap, midpoint=mid, name='shifted')
        shifted_cmap.set_bad('w')
        
        col.set(array=s, cmap=shifted_cmap)
        col.set_clip_on(False)

        ax.add_collection(col)
        
    return dict_mat


def heatmap_hybrids(M, ax, title, xlabel, ylabel, xticklabels, yticklabels, fold=False, cmap='RdBu', vmin=0.0, vmax=1.0, pad=0.25, legend_title=''):
    '''
    '''
    from matplotlib.ticker import FormatStrFormatter
    
    if fold:
        # get the matrix M and its transpose
        X = M.values
        Y = M.values.T
        # calculate the element-wise average of the two matrices
        Z = np.add(X, Y) / 2.
        Z = np.tril(Z) # get the lower triangle of the matrix
        Z = np.ma.masked_array(Z, Z == 0) # mask the upper triangle
    else:
        Z = M.values
    
    #
    Z = np.ma.array(Z, mask=np.isnan(Z))
    cmap.set_bad('0.1',1.)

    # shift colormap
    orig_cmap = cmap
    mid=(1 - np.ma.max(Z)/(np.ma.max(Z) + abs(np.ma.min(Z))))

    # shifted_cmap = utils.shift_colormap(orig_cmap, midpoint=mid, name='shifted')
    # shifted_cmap.set_bad('w') # default value is 'k'

    im = ax.pcolor(Z, edgecolors='lightgrey', linewidths=0.5, cmap=orig_cmap, vmin=vmin, vmax=vmax)
    
    # place the major ticks at the middle of each cell
    ax.set_xticks(np.arange(Z.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(Z.shape[0]) + 0.5, minor=False)

    # set tick labels
    ax.set_xticklabels(xticklabels, minor=False, rotation=90)
    ax.set_yticklabels(yticklabels, minor=False)

    # set title and x/y labels
    ax.set_title(title, fontsize=6, y=1.15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # remove last blank column
    ax.set_xlim( (0, Z.shape[1]) )
    ax.set_ylim( (0, Z.shape[0]) )
    
    # turn off all the ticks
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
        
    # proper orientation (origin at the top left instead of bottom left)
    ax.invert_yaxis()
    
    # set equal aspect ratio
    ax.set_aspect('equal')

    # add colorbar
    cax = inset_axes(ax, width='4%', height='30%', loc=3,
                     bbox_to_anchor=(1.05, 0., 1, 1),
                     bbox_transform=ax.transAxes,
                     borderpad=0)
    cbar = plt.colorbar(im, cax=cax, ticks=[vmin, 0, vmax], format='%.1f')
    cbar.ax.set_title(legend_title, horizontalalignment='center', fontsize=5)
    cbar.ax.tick_params(labelsize=5)
    cbar.locator = ticker.MaxNLocator(nbins = 3)
    cbar.outline.set_visible(False)
    

def heatmap(x, y, z, ax, title, xlabel, ylabel, xticklabels, yticklabels, cmap='RdBu', vmin=0.0, vmax=1.0, show=False):
    '''
    Inspired by:
    - http://stackoverflow.com/a/16124677/395857 
    - http://stackoverflow.com/a/25074150/395857
    '''

    # plot the heatmap
    c = ax.pcolor(x, y, z, linewidths=0, cmap=cmap, vmin=vmin, vmax=vmax)

    # place the major ticks at the middle of each cell
    ax.set_xticks(np.arange(z.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(z.shape[0]) + 0.5, minor=False)

    # set tick labels
    ax.set_xticklabels(xticklabels, minor=False, rotation=90)
    ax.set_yticklabels(yticklabels, minor=False)

    # set title and x/y labels
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Remove last blank column
    ax.set_xlim( (min(x), max(x)) )
    ax.set_ylim( (min(y), max(y)) )

    # Turn off all the ticks
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    # Proper orientation (origin at the top left instead of bottom left)
    ax.invert_yaxis()
    
    return c


def set_custom_labels(index, pos):
    """
    
    """
    start = dict((m[pos], ii) for ii,m in enumerate(index.values))
    end = dict((m[pos], len(index)-ii-1) for ii,m in enumerate(index[::-1].values))
    labels = dict((key, (start[key] + end.get(key, 0))/2.) for key in end.keys())
    
    return start, end, labels


def add_inner_title(ax, title, loc, size=None, **kwargs):
    from matplotlib.offsetbox import AnchoredText
    from matplotlib.patheffects import withStroke
    if size is None:
        size = dict(size=plt.rcParams['legend.fontsize'])
    at = AnchoredText(title, loc=loc, prop=size,
                      pad=0., borderpad=0.5,
                      frameon=False, **kwargs)
    ax.add_artist(at)
    at.txt._text.set_path_effects([withStroke(foreground="w", linewidth=3)])
    return at
    

from matplotlib.transforms import Bbox, TransformedBbox, \
    blended_transform_factory

from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector,\
    BboxConnectorPatch


def connect_bbox(bbox1, bbox2,
                 loc1a, loc2a, loc1b, loc2b,
                 prop_lines, prop_patches=None):
    if prop_patches is None:
        prop_patches = prop_lines.copy()
        prop_patches["alpha"] = prop_patches.get("alpha", 1)*0.2

    c1 = BboxConnector(bbox1, bbox2, loc1=loc1a, loc2=loc2a, **prop_lines)
    c1.set_clip_on(False)
    c2 = BboxConnector(bbox1, bbox2, loc1=loc1b, loc2=loc2b, **prop_lines)
    c2.set_clip_on(False)

    bbox_patch1 = BboxPatch(bbox1, **prop_patches)
    bbox_patch2 = BboxPatch(bbox2, **prop_patches)

    p = BboxConnectorPatch(bbox1, bbox2,
                           # loc1a=3, loc2a=2, loc1b=4, loc2b=1,
                           loc1a=loc1a, loc2a=loc2a, loc1b=loc1b, loc2b=loc2b,
                           **prop_patches)
    p.set_clip_on(False)

    return c1, c2, bbox_patch1, bbox_patch2, p


def zoom_effect(ax1, ax2, xmin, xmax, **kwargs):
    """
    ax1 : the main axes
    ax1 : the zoomed axes
    (xmin,xmax) : the limits of the colored area in both plot axes.

    connect ax1 & ax2. The x-range of (xmin, xmax) in both axes will
    be marked.  The keywords parameters will be used to create
    patches.

    """

    trans1 = blended_transform_factory(ax1.transData, ax1.transAxes)
    trans2 = blended_transform_factory(ax2.transData, ax2.transAxes)

    bbox = Bbox.from_extents(xmin, 0, xmax, 1)

    mybbox1 = TransformedBbox(bbox, trans1)
    mybbox2 = TransformedBbox(bbox, trans2)

    prop_patches = kwargs.copy()
    prop_patches["ec"] = "none"
    prop_patches["alpha"] = 0.2

    c1, c2, bbox_patch1, bbox_patch2, p = \
    connect_bbox(mybbox1, mybbox2,
    loc1a=3, loc2a=2, loc1b=4, loc2b=1,
    prop_lines=kwargs, prop_patches=prop_patches)

    ax1.add_patch(bbox_patch1)
#     ax2.add_patch(bbox_patch2)
    ax2.add_patch(c1)
    ax2.add_patch(c2)
    ax2.add_patch(p)

    return c1, c2, bbox_patch1, bbox_patch2, p


from numpy.random import *

def get_text_positions(x_data, y_data, txt_width, txt_height):
    a = zip(y_data, x_data)
    text_positions = y_data.copy()
    for index, (y, x) in enumerate(a):
        local_text_positions = [i for i in a if i[0] > (y - txt_height) 
                            and (abs(i[1] - x) < txt_width * 2) and i != (y,x)]
        if local_text_positions:
            sorted_ltp = sorted(local_text_positions)
            if abs(sorted_ltp[0][0] - y) < txt_height: #True == collision
                differ = np.diff(sorted_ltp, axis=0)
                a[index] = (sorted_ltp[-1][0] + txt_height, a[index][1])
                text_positions[index] = sorted_ltp[-1][0] + txt_height
                for k, (j, m) in enumerate(differ):
                    #j is the vertical distance between words
                    if j > txt_height * 2: #if True then room to fit a word in
                        a[index] = (sorted_ltp[k][0] + txt_height, a[index][1])
                        text_positions[index] = sorted_ltp[k][0] + txt_height
                        break
    return text_positions

def text_plotter(x_data, y_data, text_positions, axis,txt_width,txt_height):
    for x,y,t in zip(x_data, y_data, text_positions):
        axis.text(x - txt_width, 1.01*t, '%d'%int(y),rotation=0, color='blue')
        if y != t:
            axis.arrow(x, t,0,y-t, color='red',alpha=0.3, width=txt_width*0.1, 
                       head_width=txt_width, head_length=txt_height*0.5, 
                       zorder=0,length_includes_head=True)
            
            
def annotate_custom(ax, s, xy_arr=[], *args, **kwargs):
    ans = []
    an = ax.annotate(s, xy_arr[0], *args, **kwargs)
    ans.append(an)
    d = {}
    try:
        d['xycoords'] = kwargs['xycoords']
    except KeyError:
        pass
    try:
        d['arrowprops'] = kwargs['arrowprops']
    except KeyError:
        pass
    for xy in xy_arr[1:]:
        an = ax.annotate(s, xy, alpha=0.0, xytext=(0,0), textcoords=an, **d)
        ans.append(an)
    return ans
    
def custom_div_cmap(numcolors=11, name='custom_div_cmap',
                    mincol='blue', midcol='white', maxcol='red'):
    """ Create a custom diverging colormap with three colors
    
    Default is blue to white to red with 11 colors.  Colors can be specified
    in any way understandable by matplotlib.colors.ColorConverter.to_rgb()
    """

    from matplotlib.colors import LinearSegmentedColormap
    # from mpltools.color import LinearColormap
    
    cmap = LinearSegmentedColormap.from_list(name=name, 
                                            colors =[mincol, midcol, maxcol])#,
                                    # N=numcolors)
    return cmap


def adjust_spines(ax, spines):
    '''
    see http://matplotlib.org/devdocs/examples/pylab_examples/spine_placement_demo.html#pylab-examples-spine-placement-demo
    '''
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 10))  # outward by 10 points
            spine.set_smart_bounds(True)
        else:
            spine.set_color('none')  # don't draw spine

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])
 
def align_xaxis(ax1, v1, ax2, v2):
    """
    adjust ax2 xlimit so that v2 in ax2 is aligned to v1 in ax1
    see: http://stackoverflow.com/questions/7630778/matplotlib-align-origin-of-right-axis-with-specific-left-axis-value
    """
    _, x1 = ax1.transData.transform((0, v1))
    _, x2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dx = inv.transform((0, 0)) - inv.transform((0, x1-x2))
    miny, maxy = ax2.get_xlim()
    ax2.set_xlim(minx+dx, maxx+dx) 
    
       
def align_yaxis(ax1, v1, ax2, v2):
    """
    adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1
    see: http://stackoverflow.com/questions/7630778/matplotlib-align-origin-of-right-axis-with-specific-left-axis-value
    """
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    miny, maxy = ax2.get_ylim()
    ax2.set_ylim(miny+dy, maxy+dy)


def adjust_yaxis(ax,ydif,v):
    """shift axis ax by ydiff, maintaining point v at the same location"""
    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny>maxy or (-miny==maxy and dy > 0):
        nminy = miny
        nmaxy = miny*(maxy+dy)/(miny+dy)
    else:
        nmaxy = maxy
        nminy = maxy*(miny+dy)/(maxy+dy)
    ax.set_ylim(nminy+v, nmaxy+v)
