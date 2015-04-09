    """
    mshpScraper.py 
    Missouri State Highway Patrol scraper for crash data!
    [azide0x37] Alexander Templeton (nepenthe.me)
    
    Returns: pandas Data.Frame object
    
    Class usage template
    myScrape = mshpScraper()
    data = myScrape()
    """
    #web analysis
    import requests
    import urllib2
    import datetime
    import time
    from dateutil import parser
    from bs4 import BeautifulSoup
    from collections import OrderedDict 
    
    #machine learning
    import numpy as np
    import pandas as pd
    from sklearn import pipeline
    from sklearn import datasets
    from sklearn import metrics
    from sklearn.qda import QDA
    import sklearn.preprocessing
    import sklearn.cross_validation
    import sklearn.decomposition
    
    #sklearn_pandas includes
    from sklearn.base import BaseEstimator, TransformerMixin
    from sklearn import cross_validation
    from sklearn import grid_search
    import sys
    
    class mshpScraper:
        
        def __init__(
                    self,
                    url = 'http://www.mshp.dps.missouri.gov/HP68/SearchAction', 
                    colNames = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop'], 
                    county = 'Jefferson'):
    
            self._url = url
            self._colNames = colNames
            
            #Cache our response
            self._response = requests.get(self._url, headers = {'User-Agent': 'Mozilla/5.0'})
    
        def __str__(self):
            try:
                return self.url
            except:
                print "Unable to print url." 
        
        def __call__(self, refreshCache = False):
            
            if refreshCache:
                self.__init__()
            
            _souped = BeautifulSoup(self._response.text)
    
            #This is the particular table with the data we need.
            #TODO: Find a better way to pick the right one?
            _table = _souped.find('table', summary="Table listing details of the accident.")
            rows = _table.findAll('tr')
     
            _dataset = OrderedDict((self._colNames[i], []) for i in range(len(self._colNames)))
            
            for tr in rows[1:]:
                cols = tr.findAll('td')
                counter = 0
                for td in cols[1:]:
                    try:
                        text = ''.join(td.find(text=True))
                        _dataset[self._colNames[counter]].append(text)
                        counter += 1
                    except:
                        counter = 0
            
            #Attempt to coerce date and time to datetime and remove originals
            _dataset['Datetime'] = [datetime.datetime.combine(parser.parse(_dataset['Date'][row]).date(), parser.parse(_dataset['Time'][row]).time()) for row in range(len(_dataset['Date']))]
            
            #Formatted test print
            #print [datetime.datetime.strftime(_dataset['Datetime'][i], "%c") for i in range(len(_dataset['Date']))]
    
            #Ship it!
            return pd.DataFrame(_dataset)        
            
    
    #sklearn-pandas (because it was faster than importing it
    if sys.version_info >= (3, 0):
        basestring = str
    
    def cross_val_score(model, X, *args, **kwargs):
        X = DataWrapper(X)
        return cross_validation.cross_val_score(model, X, *args, **kwargs)
    
    
    class GridSearchCV(grid_search.GridSearchCV):
        def fit(self, X, *params, **kwparams):
            super(GridSearchCV, self).fit(DataWrapper(X), *params, **kwparams)
    
        def predict(self, X, *params, **kwparams):
            super(GridSearchCV, self).fit(DataWrapper(X), *params, **kwparams)
    
    try:
        class RandomizedSearchCV(grid_search.RandomizedSearchCV):
            def fit(self, X, *params, **kwparams):
                super(RandomizedSearchCV, self).fit(DataWrapper(X), *params, **kwparams)
    
            def predict(self, X, *params, **kwparams):
                super(RandomizedSearchCV, self).fit(DataWrapper(X), *params, **kwparams)
    except AttributeError:
        pass
    
    
    class DataWrapper(object):
        def __init__(self, df):
            self.df = df
    
        def __len__(self):
            return len(self.df)
    
        def __getitem__(self, key):
            return self.df.iloc[key]
    
    
    class PassthroughTransformer(TransformerMixin):
        def fit(self, X, y=None, **fit_params):
            return self
    
        def transform(self, X):
            return np.array(X).astype(np.float)
    
    
    class DataFrameMapper(BaseEstimator, TransformerMixin):
        '''
        Map Pandas data frame column subsets to their own
        sklearn transformation.
        '''
    
        def __init__(self, features):
            '''
            Params:
            features    a list of pairs. The first element is the pandas column
                        selector. This can be a string (for one column) or a list
                        of strings. The second element is an object that supports
                        sklearn's transform interface.
            '''
            self.features = features
    
    
        def _get_col_subset(self, X, cols):
            '''
            Get a subset of columns from the given table X.
            X       a Pandas dataframe; the table to select columns from
            cols    a string or list of strings representing the columns
                    to select
            Returns a numpy array with the data from the selected columns
            '''
            return_vector = False
            if isinstance(cols, basestring):
                return_vector = True
                cols = [cols]
    
            if isinstance(X, list):
                X = [x[cols] for x in X]
                X = pd.DataFrame(X)
    
            elif isinstance(X, DataWrapper):
                # if it's a datawrapper, unwrap it
                X = X.df
    
            if return_vector:
                t = X[cols[0]]
            else:
                t = X.as_matrix(cols)
    
            return t
    
    
        def fit(self, X, y=None):
            '''
            Fit a transformation from the pipeline
            X       the data to fit
            '''
            for columns, transformer in self.features:
                if transformer is not None:
                    transformer.fit(self._get_col_subset(X, columns))
            return self
    
    
        def transform(self, X):
            '''
            Transform the given data. Assumes that fit has already been called.
            X       the data to transform
            '''
            extracted = []
            for columns, transformer in self.features:
                # columns could be a string or list of
                # strings; we don't care because pandas
                # will handle either.
                if transformer is not None:
                    fea = transformer.transform(self._get_col_subset(X, columns))
                else:
                    fea = self._get_col_subset(X, columns)
    
                if hasattr(fea, 'toarray'):
                    # sparse arrays should be converted to regular arrays
                    # for hstack.
                    fea = fea.toarray()
    
                if len(fea.shape) == 1:
                    fea = np.array([fea]).T
                extracted.append(fea)
    
            # combine the feature outputs into one array.
            # at this point we lose track of which features
            # were created from which input columns, so it's
            # assumed that that doesn't matter to the model.
            return np.hstack(extracted)
            
    #Implementation
    myScrape = mshpScraper()
    data = myScrape()
    
    mapper = DataFrameMapper([
        ('Age', sklearn.preprocessing.StandardScaler()),
        ('Severity', sklearn.preprocessing.LabelBinarizer()),
        ('County', sklearn.preprocessing.LabelBinarizer()),
        ('Troop', sklearn.preprocessing.LabelBinarizer())
        ])
        
    print np.round(mapper.fit_transform(data), 2)
    pipe = sklearn.pipeline.Pipeline([('featurize', mapper), ('lm', sklearn.linear_model.LinearRegression())])
    
    #np.round(cross_val_score(pipe, data), 2)
    #print mapper
