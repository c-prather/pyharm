__license__ = """
 File: result_figures.py
 
 BSD 3-Clause License
 
 Copyright (c) 2020-2023, Ben Prather and AFD Group at UIUC
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
 
 1. Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.
 
 2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
 
 3. Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import numpy as np
import matplotlib.pyplot as plt

import pyharm
from pyharm.defs import Loci
from pyharm.util import i_of

__doc__ = \
"""Plots of post-reduction results as computed by pyharm-analysis & read by ana_results.py.
WIP.
"""

def _get_t_slice(result, arange):
    """Returns a time slice corresponding to the tuple or number 'arange'
    (optionally negative-indexed from sim end)
    """
    # TODO BOUNDS CORRECTLY
    if isinstance(arange, slice) or isinstance(arange, tuple) or isinstance(arange, list):
        try:
            return result.get_time_slice(arange[0], arange[1])
        except KeyError:
            return None
    elif arange is not None:
        # Min only, negative offset from end accepted
        try:
            return result.get_time_slice(arange)
        except KeyError:
            return None
    else:
        return True, slice(None)

def _get_r_slice(result, rrange):
    """Get a slice of radial zones matching the plot window.
    Plotting only the necessary radial range makes auto-scaling of the y-axis work
    """
    return slice(max(i_of(result['r'], rrange[0]), 0), i_of(result['r'], rrange[1]))

def _trunc_at_spin(tag):
    model_lst = tag.split(" ")
    model_lst_trunc = []
    for m in model_lst:
        if " a" in m or "$a" in m:
            break
        model_lst_trunc.append(m)
    return " ".join(model_lst_trunc)

def _model_pretty(folder):
    model = folder.split("/")
    if len(model) >= 2:
        if "_" in model[-1]:
            return model[-3]
        return model[-2].upper()+r" $"+model[-1]+r"^\circ$"
    else:
        return folder.replace("")

def _radial_profile(ax, result, var, arange=-1000, window=(1,500), disk=True, plot_std=False, plot_eh=False, selector=None, tag="",
                   print_time=False, model_shared_portion=0, plotrc={}, **kwargs):

    if selector is not None and not selector(result.tag):
        return

    model = " ".join(result.tag.split(" ")[model_shared_portion:])
    title = " ".join(result.tag.split(" ")[:model_shared_portion])

    # Get the times to average
    avg_slice = _get_t_slice(result, arange)
    times = (round(result['t'][avg_slice][0]/1000)*1000,
             round(result['t'][avg_slice][-1]/1000)*1000)
    # Get just the relevant radial slice so y-limits get set properly
    r_slice = _get_r_slice(result, (window[0]-1, window[1]+20))

    tyvals = result['rt/{}'.format(var)][avg_slice, r_slice]

    yvals = np.mean(tyvals, axis=0)
    p = ax.plot(result['r'][r_slice], yvals, label=model+("",r" {}-{} $t_g$".format(*times))[print_time], **plotrc)
    if plot_std:
        yerrs = np.std(tyvals, axis=0)
        ax.fill_between(result['r'][r_slice], yvals-yerrs, yvals+yerrs, alpha=0.5, color=p[0].get_color())

    if plot_eh:
        ax.axvline(2.0, color='k') # TODO set xlim inside despite default
    else:
        ax.set_xlim(window[0], window[1])

    ax.set_xlabel(r"Radius [$r_g$]")
    ax.set_ylabel(pyharm.pretty(var), rotation=0, ha='right')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

def _point_per_run(axis, results, var, to_plot, plot_vs, window=None, arange=-1000, selector=None, tag="",
                  print_time=False, print_only_time=False, model_shared_portion=0, no_print_flux=False, plotrc={},
                  **kwargs):
    if plot_vs == 'spin':
        get_xval = lambda model: model['a']
        get_modelname = lambda model: model.tag
    elif plot_vs == 'res':
        get_xval = lambda model: model['nx3']
        get_modelname = lambda model: model.tag

    # Dictionaries by "model" of lists by spin
    model_xvals = {}
    model_yvals = {}
    model_stds = {}
    model_times = {}
    title = ""
    # Run through the files and suck up everything, sorting by "model" not including spin
    for result in results:
        # If this thing is even readable...
        avg_slice = _get_t_slice(result, arange)
        if avg_slice is None:
            print("Skipping {}: no data fround for range {}".format(result.tag, arange))
            continue


        model = get_modelname(result)
        xval = get_xval(result)

        model = " ".join(model.split(" ")[model_shared_portion:])
        title = " ".join(model.split(" ")[:model_shared_portion])

        if selector is not None and not selector(model):
            continue

        if model not in model_xvals:
            model_xvals[model] = []
            model_yvals[model] = []
            model_stds[model] = []
            # Record times to print, to nearest 1k
            model_times[model] = (round(result['t'][avg_slice][0]/1000)*1000,
                                  round(result['t'][avg_slice][-1]/1000)*1000)
        model_xvals[model].append(xval)

        if to_plot in ('avg', 'avg_std'):
            val = np.mean(result['t/'+var][avg_slice])
            if to_plot == 'avg_std':
                model_stds[model].append(np.std(result['t/'+var][avg_slice]))
        elif to_plot == 'std':
            val = np.std(result['t/'+var][avg_slice])
        elif to_plot == 'std_rel':
            val = np.std(result['t/'+var][avg_slice]) / np.mean(result['t/'+var][avg_slice])
        model_yvals[model].append(val)
    
    # Then plot each model
    for model in model_xvals.keys():
        if print_only_time:
            mname = r"{}-{} $t_g$".format(*model_times[model])
        else:
            mname = tag + model + ("", r" ({}-{} $t_g$)".format(*model_times[model]))[print_time]
        if no_print_flux:
            mname = mname.replace("MAD","").replace("SANE","").replace("  "," ")
        if to_plot == 'avg_std':
            # Sort all arrrays by x value to avoid weird back and forth lines
            xvals, yvals, ystd = zip(*sorted(zip(model_xvals[model], model_yvals[model], model_stds[model]), key=lambda x: x[0]))
            axis.errorbar(xvals, yvals, yerr=ystd, fmt='.--', capsize=5, label=mname, **plotrc)
        else:
            xvals, yvals = zip(*sorted(zip(model_xvals[model], model_yvals[model]), key=lambda x: x[0]))
            axis.plot(xvals, yvals, '.--', label=mname, **plotrc)

    axis.set_title(title)
    axis.grid(True)

    if plot_vs == 'spin':
        axis.set_xlim(-1,1)
        axis.set_xlabel(r"Spin $a_*$")
    elif plot_vs == 'res':
        axis.set_xlabel(r"Radial resolution")
        # TODO 2^x, log?

    if window is not None:
        axis.set_xlim(window[:2])
        axis.set_ylim(window[2:])

    if to_plot in ('avg', 'avg_std'):
        axis.set_ylabel(r"$\langle" + pyharm.pretty(var, segment=True) + r"\rangle$", rotation=0, ha='right')
    elif to_plot == 'std':
        axis.set_ylabel(r"$\sigma \left(" + pyharm.pretty(var, segment=True) + r"\right)$", rotation=0, ha='right')
    elif to_plot == 'std_rel':
        axis.set_ylabel(r"$\frac{\sigma \left(" + pyharm.pretty(var, segment=True) + r"\right)}{\langle" + pyharm.pretty(var, segment=True) + r"\rangle}$", rotation=0, ha='right')

    axis.legend()

# Ready-made names: figsize, save name, etc. TODO handle kwargs not passed on to line plot
def std_vs_spin(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'std', 'spin', plotrc=plotrc, **kwargs)
    return fig
def avg_vs_spin(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'avg', 'spin', plotrc=plotrc, **kwargs)
    return fig
def avg_std_vs_spin(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'avg_std', 'spin', plotrc=plotrc, **kwargs)
    return fig

def res_study_std(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'std', 'res', plotrc=plotrc, **kwargs)
    return fig
def res_study_avg(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'avg', 'res', plotrc=plotrc, **kwargs)
    return fig
def res_study_avg_std(results, kwargs, plotrc={}):
    fig, ax = plt.subplots(1,1)
    _point_per_run(ax, results, kwargs['varlist'][0], 'avg_std', 'res', plotrc=plotrc, **kwargs)
    return fig

def default_radial_averages(results, kwargs):
    if kwargs['varlist'] is None:
        vars = ('rho', 'Pg', 'b', 'bsq', 'Ptot', 'u^3', 'sigma_post', 'inv_beta_post')
    else:
        vars = kwargs['varlist']

    # Radial profiles of variables
    nx = min(len(vars), 4)
    ny = (len(vars)-1)//4+1
    fig, _ = plt.subplots(ny, nx, figsize=(4*nx,4*ny))
    ax = fig.get_axes()
    for result in results:
        for a,var in enumerate(vars):
            window = _radial_profile(ax[a], result, var, **kwargs)

    return fig

def jet_fluxes(results, kwargs):
    if kwargs['varlist'] is None:
        vars = ('Mdot_jet', 'P_jet', 'P_EM_jet')
    else:
        vars = kwargs['varlist']

    fig, _ = plt.subplots(len(vars), 1, figsize=(7, 3*len(vars)))
    ax = fig.get_axes()
    for result in results:
        for a,var in enumerate(vars):
            window = _radial_profile(ax[a], result, var, **kwargs)
            if a < len(vars)-1:
                ax[a].set_xlabel('')
                ax[a].set_xticklabels([])
                ax[a].tick_params(length=0)
    fig.subplots_adjust(left=0.2, hspace=0.02)

    return fig

def disk_momentum(results, kwargs):
    kwargs['varlist'] = "u_3"
    return radial_averages(results, kwargs)

def _plot_eh_fluxes(ax, result, per=False, arange=None, vars=('mdot', 'phi_b', 'ldot', 'eff')):
    # TODO somehow make this less janky
    #result.diag_fns['mdot'] = lambda diag: diag['Mdot']
    #result.diag_fns['eff'] = lambda diag: diag['eff_jet50']

    for a,var in enumerate(vars):
        data = result['t/{}'.format(var)]
        if 'phi_b' in var:
            data *= np.sqrt(4*np.pi)
        pt = ax[a].plot(result['t'], data, label=result.tag)
        if arange is not None:
            # Get the times to average
            avg_slice = _get_t_slice(result, arange)
            times = (round(result['t'][avg_slice][0]/1000)*1000,
                    round(result['t'][avg_slice][-1]/1000)*1000)
            avg = np.mean(data[avg_slice])
            ax[a].hlines(avg, times[0], times[1], colors=pt[0].get_color(), linestyles='dashed')
            ax[a].text(times[1], avg, f"{avg:.2f}")
            
        ax[a].set_ylabel(pyharm.pretty(var), rotation=0, ha='right')
        ax[a].grid(True)

def _plot_eh_phi_versions(ax, result):
    for a,var in enumerate(('phi_b', 'phi_b_upper', 'phi_b_lower')):
        ax[a].plot(result['t'], result['t/{}'.format(var)], label=result.tag)
        ax[a].set_ylabel(pyharm.pretty(var), rotation=0, ha='right')
        ax[a].grid(True)
    # Additionally plot
    ax[0].plot(result['t'], np.abs(result['t/phi_b_upper'])+np.abs(result['t/phi_b_lower']), label=result.tag+" hemispheres")

def eh_phi_versions(results, kwargs):
    for result in results:
        # Event horizon fluxes
        fig, _ = plt.subplots(3,1, figsize=(7,7))
        axes = fig.get_axes()
        _plot_eh_phi_versions(axes, result)
        plt.subplots_adjust(wspace=0.4)
    return fig

def eh_fluxes(results, kwargs):
    # TODO(CEP) handle "per" here, via vars arguments
    xsize = float(kwargs['fig_x']) if kwargs['fig_x'] is not None else 10
    ysize = float(kwargs['fig_y']) if kwargs['fig_y'] is not None else 10
    fig, _ = plt.subplots(4,1, figsize=(xsize, ysize))
    ax = fig.get_axes()
    for result in results:
        _plot_eh_fluxes(ax, result, per=kwargs['per'], arange=(kwargs['arange'] if 'arange' in kwargs else None))

    ax[0].legend()
    if kwargs['ymax_eff'] is not None:
        ax[3].set_ylim(0, kwargs['ymax_eff'])
    plt.subplots_adjust(wspace=0.4)
    return fig

def jet_efficiency(results, kwargs):
    xsize = float(kwargs['fig_x']) if kwargs['fig_x'] is not None else 10
    ysize = float(kwargs['fig_y']) if kwargs['fig_y'] is not None else 3
    fig, _ = plt.subplots(1,1, figsize=(xsize, ysize))
    ax = fig.get_axes()
    for result in results:
        _plot_eh_fluxes(ax, result, per=kwargs['per'], arange=(kwargs['arange'] if 'arange' in kwargs else None), vars=('eff',))

    ax[0].legend()
    if kwargs['ymax_eff'] is not None:
        ax[3].set_ylim(0, kwargs['ymax_eff'])
    plt.subplots_adjust(wspace=0.4)
    return fig

def mdot_versions(results, kwargs):
    fig, _ = plt.subplots(3,1, figsize=(10,10))
    ax = fig.get_axes()
    for result in results:
        for a,var in enumerate(('mdot', 'Mdot', 'Mdot_5')):
            # Mdot
            ax[0].plot(result['t'], result['t/{}'.format(var)], label=f"{result.tag} {var}")
            ax[0].set_ylabel(pyharm.pretty('mdot'), rotation=0, ha='right')
            ax[0].grid(True)
            # Phi normalized on that mdot
            ax[1].plot(result['t'], result['Phi_b'] / np.sqrt(result[f'smoothed_{var}']))
            yl = r"$\frac{\Phi_{BH}}{\sqrt{\langle " + pyharm.pretty('mdot', segment=True) + r"\rangle}}$"
            ax[1].set_ylabel(yl, rotation=0, ha='right')
            ax[1].grid(True)
        # Versions of Edot
        for a,var in enumerate(('Edot', 'Edot_5')):
            ax[2].plot(result['t'], result[var] / result['smoothed_mdot'], label=f"{result.tag} {var}")
        ax[2].plot(result['t'], result['edot'], label=f"{result.tag} edot")
        fe_i = i_of(dump['r1d'], 40.)
        ax[2].plot(result['t'], result['FE'][fe_i] / result['smoothed_mdot'], label=f"{result.tag} Edot_40")
        ax[2].set_ylabel(pyharm.pretty('edot'), rotation=0, ha='right')
        ax[2].grid(True)

        # Versions of eta
        for a,var in enumerate(('Edot', 'Edot_5')):
            ax[3].plot(result['t'], result[var] / result['smoothed_mdot'], label=f"{result.tag} {var}")
        ax[3].plot(result['t'], result['edot'], label=f"{result.tag} edot")
        fe_i = i_of(dump['r1d'], 40.)
        ax[3].plot(result['t'], result['FE'][fe_i] / result['smoothed_mdot'], label=f"{result.tag} Edot_40")
        ax[3].set_ylabel(pyharm.pretty('edot'), rotation=0, ha='right')
        ax[3].grid(True)

    ax[0].legend()
    ax[2].legend()
    plt.subplots_adjust(wspace=0.4)
    return fig
