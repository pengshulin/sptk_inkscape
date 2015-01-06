#!/usr/bin/env python
# render lcd snapshots (part of SPTK)
# designed by Peng Shulin <trees_peng@163.com>
import os, sys, optparse, tempfile

def main(argv=None):
    if argv is None:
        argv = sys.argv
    #sys.path.append('.')
   
    parser = optparse.OptionParser(
        usage = "%prog --svg=<svg_file>",
        description = 'sptk lcd snapshots render')

    parser.add_option( '--svg',
        dest = 'svg',
        action = 'store',
        type = 'string',
        help = 'input svg file template')

    parser.add_option( '--width',
        dest = 'width',
        action = 'store',
        type = 'int',
        help = 'output file width')

    parser.add_option( '--height',
        dest = 'height',
        action = 'store',
        type = 'int',
        help = 'output file height')

    parser.add_option( '--filetype',
        dest = 'filetype',
        action = 'store',
        default = 'png',
        type = 'choice',
        choices = ['png', 'ps', 'eps', 'pdf'],
        help = 'output file type')

    parser.add_option( '--sptkdir',
        dest = 'sptkdir',
        action = 'store',
        default = '.',
        type = 'string',
        help = 'the directory to import sptk data')

    parser.add_option( '--skip',
        dest = 'skip',
        action = 'store_true',
        default = False,
        help = 'skip existing image file')

 
    (options, args) = parser.parse_args(argv[1:])
    
    if options.svg is None:
        print >>sys.stderr, "Svg file needed"
        return 1

    sys.path.append(options.sptkdir)

    # import   
    try:
        from sptk_lcd_segment import segments
    except ImportError:
        print >>sys.stderr, "Failed to import sptk_lcd_segment.py"
        return 1
    try:
        from sptk_lcd_snapshot_data import snapshots
    except ImportError:
        print >>sys.stderr, "Failed to import sptk_lcd_snapshot_data.py"
        return 1
  
    # temp svg file 
    tempsvg = tempfile.mktemp(suffix='.svg', prefix='sptk_', dir='/dev/shm') 
    tempsvg2 = tempfile.mktemp(suffix='.svg', prefix='sptk_', dir='/dev/shm') 

    # render an empty template with all lcd segments off
    cmd = 'sptk_lcd_clear.py ' + ' '.join(['--id=%s'% segments[i] for i in segments])
    cmd += ' %s > %s'% (options.svg, tempsvg)
    #print cmd
    os.system( cmd )

    for s in snapshots:
        name = s['name']
        flags = s['flags']
        print 'Rendering %s...'% name
        ids = [segments[i] for i in flags] 

        if options.skip and os.path.isfile('%s.%s'% (name, options.filetype)):
            continue

        # render target svg file
        cmd = 'sptk_lcd_set.py ' + ' '.join(['--id=%s'%i for i in ids]) 
        cmd += ' %s > %s'% (tempsvg, tempsvg2)
        #print cmd
        os.system( cmd )

        # render output img
        cmd = 'inkscape --export-%s=%s.%s'% (options.filetype, name, options.filetype)
        if options.width:
            cmd += ' --export-width=%d'% options.width
        if options.height:
            cmd += ' --export-height=%d'% options.height
        cmd += ' %s'% tempsvg2
        #print cmd
        os.system( cmd )
        print 'Done'
   
    os.remove( tempsvg ) 
    if os.path.isfile(tempsvg2):
        os.remove( tempsvg2 ) 
    return 0


if __name__ == '__main__':
    sys.exit(main())


