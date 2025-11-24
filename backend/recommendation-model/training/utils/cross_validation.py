from sklearn.model_selection import GroupKFold
import numpy as np
import lightgbm as lgb

# K fold cross validation for reranking model
def tune_hyperparamaters_cv(groups, X, y, n_splits: int = 5):
    # group labels for groupkfold (one label per sample indicating which user it belongs to)
    group_labels = []
    for user_idx, group_size in enumerate(groups):
        group_labels.extend([user_idx] * group_size)
    
    group_labels = np.array(group_labels)

    print(f"Total samples: {len(X)}, Total users: {len(groups)}")

    # parameter grid to search
    param_grid = [
        {'n_estimators': 50, 'learning_rate': 0.05, 'num_leaves': 31, 'max_depth': 5, 'min_child_samples': 20},
        {'n_estimators': 100, 'learning_rate': 0.05, 'num_leaves': 31, 'max_depth': 6, 'min_child_samples': 20},
        {'n_estimators': 100, 'learning_rate': 0.1, 'num_leaves': 31, 'max_depth': 6, 'min_child_samples': 10},
        {'n_estimators': 150, 'learning_rate': 0.05, 'num_leaves': 63, 'max_depth': 8, 'min_child_samples': 20},
        {'n_estimators': 200, 'learning_rate': 0.01, 'num_leaves': 31, 'max_depth': 6, 'min_child_samples': 30},
        {'n_estimators': 100, 'learning_rate': 0.05, 'num_leaves': 15, 'max_depth': 5, 'min_child_samples': 20},
        {'n_estimators': 150, 'learning_rate': 0.08, 'num_leaves': 63, 'max_depth': 8, 'min_child_samples': 20, 'feature_fraction': 0.8, 'bagging_fraction': 0.8, 'bagging_freq': 5}
    ]

    best_score = 0
    best_params = None
    best_std = 0

    for params in param_grid:
        print(f"\n{'='*80}")
        print(f"Testing params: {params}")
        print('='*80)

        fold_scores = []
        gkf = GroupKFold(n_splits=n_splits)

        for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=group_labels)):
            print(f"\nFold {fold_idx + 1}/{n_splits}")

            # split data
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # compute groups for train and val
            train_groups = group_labels[train_idx]
            val_groups = group_labels[val_idx]

            # count samples per user in train/val
            groups_train = np.bincount(train_groups)
            groups_train = groups_train[groups_train > 0] # remove zeroes

            groups_val = np.bincount(val_groups)
            groups_val = groups_val[groups_val > 0] # remove zeroes

            print(f"  Train: {len(X_train)} samples, {len(groups_train)} users")
            print(f"  Val: {len(X_val)} samples, {len(groups_val)} users")

            # create LightGBM datasets
            train_data = lgb.Dataset(X_train, label=y_train, group=groups_train)
            val_data = lgb.Dataset(X_val, label=y_val, group=groups_val, reference=train_data)

            # train model
            model_params = {
                'objective': 'lambdarank',
                'metric': 'ndcg',
                'ndcg_eval_at': [1, 5, 10],
                'label_gain': [0, 1, 2, 3, 5, 7, 10, 13, 17, 22, 28],  # label gain to emphasize higher ratings (4, 5) more
                'boosting_type': 'gbdt',
                'random_state': 42,
                'verbosity': -1,
                **params
            }

            model = lgb.train(
                model_params,
                train_data,
                num_boost_round=params['n_estimators'],
                valid_sets=[val_data],
                valid_names=['valid_0'],
                callbacks=[
                    lgb.early_stopping(stopping_rounds=10),
                    lgb.log_evaluation(period=0)
                ]
            )

            # get best val score
            best_ndcg = model.best_score['valid_0']['ndcg@10']
            fold_scores.append(best_ndcg)
            print(f"  Best NDCG@10: {best_ndcg:.4f} (iteration {model.best_iteration})")
        
        # calculate mean and std
        avg_score = np.mean(fold_scores)
        std_score = np.std(fold_scores)
        print(f"\n{'-'*80}")
        print(f"Results: NDCG@10 = {avg_score:.4f} ± {std_score:.4f}")
        print(f"Fold scores: {[f'{s:.4f}' for s in fold_scores]}")
        print(f"{'-'*80}")

        # update params
        if avg_score > best_score:
            best_score = avg_score
            best_std = std_score
            best_params = params
        
    print(f"\n{'='*80}")
    print(f"BEST PARAMETERS:")
    print(f"{'='*80}")
    for key, value in best_params.items():
        print(f"  {key}: {value}")
    print(f"\nBest CV NDCG@10: {best_score:.4f} ± {best_std:.4f}")
    print(f"{'='*80}\n")

    return best_params