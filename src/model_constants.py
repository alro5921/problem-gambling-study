RF_GRID = {'max_depth': [3, 5, None],
            'max_features': ['sqrt', 'log2', None],
            'min_samples_split': [2, 4, 8],
            'min_samples_leaf': [1, 5, 10, 20],
            'bootstrap': [True, False],
            'n_estimators': [50, 100, 200],
            'random_state': [1]}

GRAD_BOOST_GRID = {'learning_rate': [0.01, 0.001, 0.0001],
                                'max_depth': [3, 5],
                                'min_samples_leaf': [5, 10, 50, 100, 200],
                                'max_features': [2, 3, 5],
                                'n_estimators': [150, 300, 500],
                                'random_state': [1]}

GRAD_GS_GUESS = {'learning_rate': .001, 'max_depth': 3, 'n_estimators': 300, 
                'min_samples_leaf': 5, 'max_features': 5}

RF_GS_GUESS = {'random_state': 1, 'n_estimators': 200, 'min_samples_split': 4, 
                    'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': None}

DEFAULT_GRID_PARAMS = {'n_iter' : 100, 'n_jobs' : -1, 'cv' : 5}