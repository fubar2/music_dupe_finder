"""
some duplicate tracks with odd hi bit characters remain in my music collection
so scan each folder looking for same sized tracks, one with a high bit set
report and optionally delete
"""

import os

MAXL=8


# see https://www.python-course.eu/levenshtein_distance.php
def iterative_levenshtein(s, t, costs=(1, 1, 1)):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t

        costs: a tuple or a list with three integers (d, i, s)
               where d defines the costs for a deletion
                     i defines the costs for an insertion and
                     s defines the costs for a substitution
    """
    rows = len(s)+1
    cols = len(t)+1
    deletes, inserts, substitutes = costs

    dist = [[0 for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for row in range(1, rows):
        dist[row][0] = row * deletes
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for col in range(1, cols):
        dist[0][col] = col * inserts

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = substitutes
            dist[row][col] = min(dist[row-1][col] + deletes,
                                 dist[row][col-1] + inserts,
                                 dist[row-1][col-1] + cost) # substitution

    return dist[row][col]




class track():
    """ structure to keep track of individual files in music folder
    """
    def __init__(self,fpath):
        self.fpath = fpath
        self.fname = os.path.split(fpath)[-1]
        self.fsize = os.path.getsize(fpath)
        self.highbit = False
        self.isdupename = False
        for c in self.fname:
            if (ord(c) > 127) or (ord(c) < 0):
                self.highbit = True
                break

    def hashigh(self):
        return self.highbit

    def isdupe(self):
        return self.isdupename

    def sizeof(self):
        return self.fsize

    def setdupe(self,dup):
        self.isdupename = dup

    def __repr__(self):
        s = 'track(fpath:%r,hibit=%r,size=%r,isdupename=%r)' % (self.fpath,self.highbit,self.fsize,self.isdupename)
        return s



class mfold():
    """ keep track of each folder full of tracks
    """
    def __init__(self,dirname,flist):
        self.dirname = dirname
        self.ignores = ['jpg','pdf','png','gif','cue','','txt']
        self.tracks = {}
        self.sizes = {}
        fflist = [x for x in flist if not x.split('.')[-1] in self.ignores]
        tn = [os.path.split(fname)[-1] for fname in fflist ]
        self.tracknames = [x for x in tn]
        self.tracksizes = [os.path.getsize(os.path.join(self.dirname,x)) for x in fflist]
        for i in range(len(self.tracknames)):
            t = self.tracknames[i]
            tr = track(os.path.join(self.dirname,fflist[i]))
            self.tracks.setdefault(t,None)
            if self.tracks[t] == None:
                self.tracks[t] = tr
            else:
                self.tracks[t].setdupe(True)
            self.sizes.setdefault(tr.fsize,None)
            if self.sizes[tr.fsize] == None:
                self.sizes[tr.fsize] = [t,]
            else:
                firstname = self.sizes[tr.fsize][0]
                leven = iterative_levenshtein(firstname,t)
                if leven <= MAXL:
                    if firstname[:3] <> t[:3] and (firstname[:3] <> '00.' and t[:3] <> '00.'):
                        print '############################# warning - first 3 chars do not match and not "00."'
                        print '***LD=%d, %s NOT added as dupe for \n***%s\n' % (leven,t,firstname)
                    else:
                        self.sizes[tr.fsize].append(t)
                        print '***LD=%d, %s added as dupe for \n***%s\n' % (leven,t,firstname)
                else:
                    print '###LD=%d, %s not added as dupe for \n###%s\n' % (leven,t,firstname)

    def gettracks(self):
        return self.tracks

    def getdupetimes(self):
        l = []
        for s in self.sizes.keys():
            if len(self.sizes[s]) > 1:
                ss = '### dupe sizes in %s: %s' % (self.dirname,self.sizes[s])
                l.append(ss)
        return '\n'.join(l)

    def makerm(self):
        """ tricky - script remove all but shortest name of dupes with same first 10 or last 10 chars
        """
        l = []
        for s in self.sizes.keys():
            dl = self.sizes[s]
            if len(dl) > 1:
                ddl = [[len(x),x] for x in dl] # decorate
                ddl.sort()
                dl = [x[1] for x in ddl] # undecorate
                l.append('\n###"%s" being left on disk' % os.path.join(self.dirname,dl[0]))
                for fn in dl[1:]: # leave shortest one
                    rms = r'rm "%s"' % os.path.join(self.dirname,fn)
                    l.append(rms)
        return '\n'.join(l)



    def __repr__(self):
        l = ['%s:' % self.dirname]
        for t in self.tracks.values():
            s = t.__repr__()
            l.append(s)
        return l

if __name__ == "__main__":
    d = '/data/Music/baroque'
    ofn = 'finddupetracks.xls'
    sfn = 'rmdupetracks.sh'
    o = open(ofn,'w')
    s = open(sfn,'w')
    for dirName, subdirList, fileList in os.walk(d):
        m = mfold(dirName, fileList)
        l = m.getdupetimes()
        if len(l) > 0:
            o.write(l)
            o.write('\n')
        l = m.makerm()
        if len(l) > 0:
            s.write(l)
            s.write('\n')
    o.close()
    s.close()





