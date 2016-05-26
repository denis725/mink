import pytest
from sklearn.grid_search import GridSearchCV

from mink import NeuralNetClassifier
from mink.layers import DenseLayer
from mink.layers import InputLayer


class TestSetParams:
    def test_set_params_2_layers_no_names(self):
        l0 = InputLayer()
        l1 = DenseLayer(l0)

        l1.set_params(num_units=567)
        assert l1.num_units == 567

        l1.set_params(incoming__Xs=123)
        assert l0.Xs == 123

    def test_set_params_2_named_layers(self):
        l0 = InputLayer(name='l0')
        l1 = DenseLayer(l0, name='l1')

        l1.set_params(num_units=567)
        assert l1.num_units == 567

        l1.set_params(incoming__Xs=123)
        assert l0.Xs == 123

        l1.set_params(l0__Xs=234)
        assert l0.Xs == 234

    def test_set_params_3_layers_only_first_named(self):
        l0 = InputLayer(name='l0')
        l1 = DenseLayer(l0)
        l2 = DenseLayer(l1, name='l1')

        l2.set_params(incoming__incoming__Xs=123)
        assert l0.Xs == 123

        l2.set_params(l0__Xs=345)
        assert l0.Xs == 345

    def test_set_params_neural_net_layers_not_named(self):
        l0 = InputLayer()
        l1 = DenseLayer(l0)
        l2 = DenseLayer(l1)
        net = NeuralNetClassifier(layer=l2)

        net.set_params(layer__num_units=123)
        assert l2.num_units == 123

        net.set_params(layer__incoming__incoming__Xs=234)
        assert l0.Xs == 234

    def test_set_params_neural_net_named_layers(self, clf_net):
        clf_net.set_params(output__num_units=234)
        assert clf_net.layer.num_units == 234

        clf_net.set_params(dense__num_units=555)
        assert clf_net.layer.incoming.num_units == 555

        clf_net.set_params(input__Xs=432)
        assert clf_net.layer.incoming.incoming.Xs == 432

    @pytest.mark.xfail
    def test_set_params_mixed_named_and_unnamed_layers(self):
        # The (perhaps irrelevant) use case of mixing named and
        # unnamed layer names in set params does not work at the
        # moment.
        l0 = InputLayer(name='l0')
        l1 = DenseLayer(l0, name='l1')
        l2 = DenseLayer(l1, name='l2')

        l2.set_params(l2__incoming__Xs=777)
        assert l0.Xs == 777


class TestNeuralNetFit:
    def test_call_fit_repeatedly(self, clf_net, clf_data):
        X, y = clf_data

        clf_net.fit(X, y, num_epochs=15)
        accuracy_before = (y == clf_net.predict(X)).mean()

        clf_net.fit(X, y, num_epochs=5)
        accuracy_after = (y == clf_net.predict(X)).mean()

        # after continuing fit, accuracy should decrease
        assert accuracy_after < accuracy_before


class TestGridSearch:
    @pytest.fixture
    def param_grid(self):
        return {
            'update__learning_rate': [0.1, 0.5],
            'max_epochs': [3, 5],
            'dense__num_units': [10, 20],
        }

    def test_grid_search(self, clf_net, clf_data, param_grid):
        X, y = clf_data

        gs = GridSearchCV(
            clf_net,
            param_grid,
            cv=3,
            scoring='accuracy',
            refit=False,
        )
        gs.fit(X, y)
