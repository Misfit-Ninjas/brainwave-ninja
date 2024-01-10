from backend.services.neurons.config import machine_learning


class TestRun:
    def test_it_should_return_the_config(self):
        config = machine_learning.Config(
            forecasting_approach=machine_learning.ForecastingApproachEnum.ML
        )
        assert machine_learning.run(config) == config
