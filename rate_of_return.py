import math,code,locale
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.ticker import FuncFormatter


locale.setlocale(locale.LC_NUMERIC, '')
locale.setlocale(locale.LC_ALL, '' )

## num periods
periods = 30
principal = 100000
increment = 0
rate = 6
delta = 0.2
contribution = 0
axcolor = 'lightgoldenrodyellow'
inflation = 2

# np.fv(rate, nper, pmt, pv, when='end')
# todo, do pv by inflation
# numpy.pv(rate, nper, pmt, fv=0.0, when='end')

def money(x, pos):
	return unicode(locale.currency(int(x), grouping=True), 'utf-8')

def calc_compounding ( _rate, _periods, _principal, _contribution, _delta, _inflation ) :
	in_rate = 0.01 * _rate
	in_delta   = 0.01 * _delta
	in_contrib = -1* _contribution
	in_princ   = -1* _principal
	in_inflation = 0.01* inflation
	print("rate %g, periods %g, principal %g, contribution %g, delta %g, inflation %g" %( _rate, _periods, in_princ, in_contrib, _delta, _inflation))
	cf1 = np.array([round(np.fv(in_rate, i, in_contrib, in_princ, when='end'),2) for i in range(1,periods+1)])
	cf2 = np.array([round(np.fv((in_rate-in_delta), i, in_contrib, in_princ, when='end'),2) for i in range(1,periods+1)])
	if _inflation == 0:
		return(np.subtract(cf1,cf2))
	else:
		diff = np.subtract(cf1,cf2)
		return np.array([round(np.pv(in_inflation, i, 0, (-1*diff[i])),2)  for i in range(_periods)])

def reset(event):
	rate_slider.reset()
	delta_slider.reset()

def update(val):
	global rate
	global delta

	rate = rate_slider.val
	delta = delta_slider.val

	## calc ydata and set it
	s = calc_compounding ( rate, periods, principal, contribution, delta,inflation )
	t = np.arange(2014, (2014+periods))
	l.set_ydata(s)
	l.set_xdata(t)
	ax.axis([2014, (2014+periods+5), 0, ((math.ceil(s.max()/10000)+1)*10000)])
	fig.canvas.draw_idle()

def contribution_update(label):
	global contribution
	print("called contrib_update")
	contribution = locale.atof(label)
	new_rate = rate_slider.val
	new_delta = delta_slider.val
	print("contrib is ", contribution)
	## calc ydata and set it
	s = calc_compounding ( new_rate, periods, principal, contribution, new_delta,0 )
	t = np.arange(2014, (2014+periods))
	l.set_ydata(s)
	l.set_xdata(t)
	ax.axis([2014, (2014+periods+5), 0, ((math.ceil(s.max()/10000)+1)*10000)])
	fig.canvas.draw_idle()

def setup_plot():
	global rate_slider, delta_slider, fig, ax, l, radio
	fig, ax = plt.subplots()
	ax.grid('on')
	plt.subplots_adjust(left=0.25, bottom=0.25)
	moneyFmt = FuncFormatter(money)
	ax.yaxis.set_major_formatter(moneyFmt)

	s = calc_compounding( rate, periods, principal, contribution, delta,inflation)
	t = np.arange(2014, (2014+periods))
	l, = plt.plot(t,s, lw=2, color='red')
	plt.ylabel("Investment Loss (FV)")
	plt.axis([2014, (2014+periods), 0, principal])
	plt.axis('tight')

	axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
	axamp  = plt.axes([0.25, 0.15, 0.65, 0.03], axisbg=axcolor)

	rate_slider = Slider(axfreq, 'Avg.Returns', 4, 8, valinit=rate)
	delta_slider = Slider(axamp, 'Delta', 0.1, 1, valinit=delta)
	resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
	button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
	rate_slider.on_changed(update)
	delta_slider.on_changed(update)
	button.on_clicked(reset)
	rax = plt.axes([0.015, 0.15, 0.15, 0.15], axisbg=axcolor)
	radio = RadioButtons(rax, ('0','3000', '6000', '9000'), active=0)
	radio.on_clicked(contribution_update)
	plt.show()
	return rate_slider,delta_slider,fig,ax,l,radio


#rate_slider,delta_slider,fig,ax,l,radio =
setup_plot()

code.interact(local=locals())
