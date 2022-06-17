# Copyright (c) 2021 rdbende <rdbende@gmail.com>

# The Forest theme is a beautiful and modern ttk theme inspired by Excel.

package require Tk 8.6

namespace eval ttk::theme::obj2pbt {

    variable version 1.0
    package provide ttk::theme::obj2pbt $version
    variable colors
    array set colors {
        -fg             "#F0F0F0"
        -bg             "#000000"
        -disabledfg     "#313131"
        -disabledbg     "#ffffff"
        -selectfg       "#ffffff"
        -selectbg       "#FF392B"
    }

    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.png] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file -format png]
        }
    }

    LoadImages [file join [file dirname [info script]] theme]

    # Settings
    ttk::style theme create obj2pbt -parent default -settings {
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertwidth 1 \
            -insertcolor $colors(-fg) \
            -fieldbackground $colors(-selectbg) \
            -font {TkDefaultFont 10} \
            -borderwidth 1 \
            -relief flat

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]

        tk_setPalette background [ttk::style lookup . -background] \
            foreground [ttk::style lookup . -foreground] \
            highlightColor [ttk::style lookup . -focuscolor] \
            selectBackground [ttk::style lookup . -selectbackground] \
            selectForeground [ttk::style lookup . -selectforeground] \
            activeBackground [ttk::style lookup . -selectbackground] \
            activeForeground [ttk::style lookup . -selectforeground]
        
        option add *font [ttk::style lookup . -font]


        # Layouts
        ttk::style layout TButton {
            Button.button -children {
                Button.padding -children {
                    Button.label -side left -expand true
                } 
            }
        }

        ttk::style layout Accent.TButton {
            AccentButton.button -children {
                AccentButton.padding -children {
                    AccentButton.label -side left -expand true
                } 
            }
        }

        ttk::style layout TCheckbutton {
            Checkbutton.button -children {
                Checkbutton.padding -children {
                    Checkbutton.indicator -side left
                    Checkbutton.label -side right -expand true
                }
            }
        }

        ttk::style layout Vertical.TScrollbar {
            Vertical.Scrollbar.trough -sticky ns -children {
                Vertical.Scrollbar.thumb -expand true
            }
        }

        ttk::style layout Horizontal.TSeparator {
            Horizontal.separator -sticky nswe
        }

        ttk::style layout Vertical.TSeparator {
            Vertical.separator -sticky nswe
        }

        # Elements

        # Button
        ttk::style configure TButton -padding {8 4 8 4} -width -10 -anchor center

        ttk::style element create Button.button image \
            [list $I(rect-basic) \
                {selected disabled} $I(rect-basic) \
                disabled $I(rect-basic) \
                selected $I(rect-basic) \
                pressed $I(rect-basic) \
                active $I(rect-hover) \
            ] -border 4 -sticky nsew

        # Arrow Cycle Button
        ttk::style configure cycle.TButton -padding {0 0 0 0} -width -10 -anchor center

        # Checkbutton
        ttk::style configure TCheckbutton -padding 4

        ttk::style element create Checkbutton.indicator image \
            [list $I(check-unsel-accent) \
                {alternate disabled} $I(check-tri-basic) \
                {selected disabled} $I(check-basic) \
                disabled $I(check-unsel-basic) \
                {pressed alternate} $I(check-tri-hover) \
                {active alternate} $I(check-tri-hover) \
                alternate $I(check-tri-accent) \
                {pressed selected} $I(check-hover) \
                {active selected} $I(check-hover) \
                selected $I(check-accent) \
                {pressed !selected} $I(check-unsel-pressed) \
                active $I(check-unsel-hover) \
            ] -width 26 -sticky w

        # Scrollbar
        ttk::style element create Horizontal.Scrollbar.trough image $I(hor-basic) \
            -sticky ew

        ttk::style element create Horizontal.Scrollbar.thumb image \
            [list $I(hor-accent) \
                disabled $I(hor-basic) \
                pressed $I(hor-hover) \
                active $I(hor-hover) \
            ] -sticky ew

        ttk::style element create Vertical.Scrollbar.trough image $I(vert-basic) \
            -sticky ns

        ttk::style element create Vertical.Scrollbar.thumb image \
            [list $I(vert-accent) \
                disabled  $I(vert-basic) \
                pressed $I(vert-hover) \
                active $I(vert-hover) \
            ] -sticky ns

        # Progressbar
        ttk::style element create Horizontal.Progressbar.trough image $I(hor-basic) \
            -sticky ew

        ttk::style element create Horizontal.Progressbar.pbar image $I(hor-accent) \
            -sticky ew

        ttk::style element create Vertical.Progressbar.trough image $I(vert-basic) \
            -sticky ns

        ttk::style element create Vertical.Progressbar.pbar image $I(vert-accent) \
            -sticky ns

        # Entry
        ttk::style element create Entry.field image \
            [list $I(border-basic) \
                {focus hover} $I(border-accent) \
                invalid $I(border-invalid) \
                disabled $I(border-basic) \
                focus $I(border-accent) \
                hover $I(border-hover) \
            ] -border 5 -padding {8} -sticky nsew

        # Separator
        ttk::style element create Horizontal.separator image $I(separator)

        ttk::style element create Vertical.separator image $I(separator)

        # Sashes
        #ttk::style map TPanedwindow -background [list hover $colors(-bg)]
    }
}
