from ta_strategies_TVLibrary import *

import pandas as pd
import numpy as np
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _run_single_strategy(strategy_item, df, append, ta_indicator_value, signal_score, signal_value, signal_explanation):
    """
    Helper function to run a single strategy in parallel.
    Returns tuple of (strategy_name, result_dataframe)
    """
    name, instance = strategy_item
    try:
        result_df = instance.run_all_strategies(
            df,
            append=append,
            ta_indicator_value=ta_indicator_value,
            signal_score=signal_score,
            signal_value=signal_value,
            signal_explanation=signal_explanation
        )
        return name, result_df
    except Exception as e:
        logger.error(f"Error running strategy {name}: {e}")
        # Return empty dataframe on error to maintain consistency
        return name, pd.DataFrame()


class AllStrategies:
    def __init__(self, max_workers=4):
        # List all strategy classes
        strategy_classes = [
            AberrationStrategies,
            AbsolutePriceOscillatorStrategies,
            AccelerationBandsStrategies,
            AccumulationDistributionLineStrategies,
            AccumulationDistributionIndexStrategies,
            AccumulationDistributionOscillatorStrategies,
            AdaptivePriceZoneStrategies,
            AllMovingAverageStrategies,
            ArcherMovingAveragesTrendsStrategies,
            ArcherOnBalanceVolumeStrategies,
            ArnaudLegouxMovingAverageStrategies,
            AroonStrategies,
            AroonOscillatorStrategies,
            AverageDirectionalIndexStrategies,
            AveragePriceStrategies,
            AverageTrueRangeStrategies,
            AwesomeOscillatorStrategies,
            BalanceOfPowerStrategies,
            BiasStrategies,
            BRARStrategies,
            BollingerBandsStrategies,
            BollingerBandsWidthStrategies,
            BullBearPowerStrategies,
            BuyAndSellPressureStrategies,
            CenterOfGravityStrategies,
            ChandeForecastOscillatorStrategies,
            ChandeKrollStopStrategies,
            ChandeMomentumOscillatorStrategies,
            ChandelierExitStrategies,
            ChaikinADLineStrategies,
            ChaikinADOscillatorStrategies,
            ChaikinMoneyFlowStrategies,
            ChaikinOscillatorStrategies,
            ChoppinessIndexStrategies,
            CommodityChannelIndexStrategies,
            CorrelationTrendIndicatorStrategies,
            CoppockCurveStrategies,
            CumulativeForceIndexStrategies,
            CrossSignalsStrategies,
            DecayStrategies,
            DecreasingPriceStrategies,
            DetrendedPriceOscillatorStrategies,
            DirectionalMovementStrategies,
            DonchianChannelStrategies,
            DoubleExponentialMovingAverageStrategies,
            EhlersSuperSmootherFilterStrategies,
            ElderRayIndexStrategies,
            EldersForceIndexStrategies,
            EldersThermometerStrategies,
            ElasticVolumeMovingAverageStrategies,
            ElasticVolumeMACDStrategies,
            ExponentialMovingAverageStrategies,
            FibonacciPivotPointsStrategies,
            FibonacciWeightedMovingAverageStrategies,
            FiniteVolumeElementStrategies,
            FisherTransformStrategies,
            ForceIndexStrategies,
            FractalAdaptiveMovingAverageStrategies,
            GannHighLowActivatorStrategies,
            HighLowAverageStrategies,
            HilbertTransformDominantCyclePeriodStrategies,
            HilbertTransformDominantCyclePhaseStrategies,
            HilbertTransformInstantaneousTrendlineStrategies,
            HilbertTransformPhasorComponentsStrategies,
            HilbertTransformSineWaveStrategies,
            HilbertTransformTrendCycleStrategies,
            HoltWinterChannelStrategies,
            HoltWinterMovingAverageStrategies,
            HullExponentialMovingAverageStrategies,
            HullMovingAverageStrategies,
            IchimokuCloudStrategies,
            IncreasingPriceStrategies,
            InertiaStrategies,
            InverseFisherTransformRSIStrategies,
            JurikMovingAverageStrategies,
            KDJIndicatorStrategies,
            KaufmanAdaptiveMovingAverageStrategies,
            KaufmanEfficiencyIndicatorStrategies,
            KeltnerChannelStrategies,
            KlingerVolumeOscillatorStrategies,
            KnowSureThingStrategies,
            LinearRegressionStrategies,
            LinearRegressionAngleStrategies,
            LinearRegressionInterceptStrategies,
            LinearRegressionSlopeStrategies,
            LongRunStrategies,
            MarkWhistlersWAVEPMStrategies,
            MarketMomentumStrategies,
            MassIndexStrategies,
            McGinleyDynamicStrategies,
            MedianPriceStrategies,
            MidPointOverPeriodStrategies,
            MidpointPricePeriodStrategies,
            MinusDirectionalIndicatorStrategies,
            MinusDirectionalMovementStrategies,
            MoneyFlowIndexStrategies,
            MomentumStrategies,
            MomentumBreakoutBandsStrategies,
            MACDStrategies,
            MovingStandardDeviationStrategies,
            NegativeVolumeIndexStrategies,
            NormalizedAverageTrueRangeStrategies,
            NormalizedBASPStrategies,
            OnBalanceVolumeStrategies,
            OHLC_AverageStrategies,
            ParabolicStopAndReverseStrategies,
            PascalsWeightedMovingAverageStrategies,
            PercentBStrategies,
            PercentagePriceOscillatorStrategies,
            PercentageVolumeOscillatorStrategies,
            PivotPointsStrategies,
            PlusDirectionalIndicatorStrategies,
            PlusDirectionalMovementStrategies,
            PositiveVolumeIndexStrategies,
            PrettyGoodOscillatorStrategies,
            PriceDistanceStrategies,
            PriceVolumeRankStrategies,
            PriceVolumeTrendStrategies,
            PriceVolumeStrategies,
            PsychologicalLineStrategies,
            QStickStrategies,
            QuantitativeQualitativeEstimationStrategies,
            RateOfChangeStrategies,
            RelativeStrengthIndexStrategies,
            RelativeStrengthXtraStrategies,
            RelativeVigorIndexStrategies,
            RelativeVolatilityIndexStrategies,
            SchaffTrendCycleStrategies,
            ShortRunStrategies,
            SineWeightedMovingAverageStrategies,
            SlopeStrategies,
            SmiErgodicOscillatorStrategies,
            SmoothedExponentialMovingAverageStrategies,
            SmoothedSimpleMovingAverageStrategies,
            SqueezeStrategies,
            SqueezeProStrategies,
            StandardDeviationStrategies,
            StochasticStrategies,
            StochasticFastStrategies,
            StochasticOscillatorStrategies,
            StochasticOscillatorKStrategies,
            StochasticRSIStrategies,
            StochasticOscillatorDStrategies,
            StopAndReverseStrategies,
            SummationStrategies,
            SupertrendStrategies,
            SymmetricWeightedMovingAverageStrategies,
            T3MovingAverageStrategies,
            TDSequentialStrategies,
            TrendSignalsStrategies,
            TriangularMovingAverageStrategies,
            TripleExponentialMovingAverageOscillatorStrategies,
            TrixStrategies,
            TwiggsMoneyIndexStrategies,
            TTMTrendStrategies,
            TypicalPriceStrategies,
            UltimateOscillatorStrategies,
            UlcerIndexStrategies,
            UpDownStrategies,
            VariableIndexDynamicAverageStrategies,
            VarianceStrategies,
            VerticalHorizontalFilterStrategies,
            VolumeAdjustedMovingAverageStrategies,
            VolumeFlowIndicatorStrategies,
            VolumePriceTrendStrategies,
            VolumeWeightedAveragePriceStrategies,
            VolumeWeightedMovingAverageStrategies,
            VolumeWeightedMACDStrategies,
            VortexIndicatorStrategies,
            WaveTrendOscillatorStrategies,
            WeightedClosingPriceStrategies,
            WeightedMovingAverageStrategies,
            WeightedOnBalanceVolumeStrategies,
            WilliamsRStrategies,
            WildersMovingAverageStrategies,
            ZeroLagExponentialMovingAverageStrategies,
            ZeroLagSimpleMovingAverageStrategies,
        ]
        # Instantiate each strategy and store the instance in a dictionary
        self.strategy_instances = {}
        for cls in strategy_classes:
            self.strategy_instances[cls.__name__] = cls()
        
        # Set max_workers for parallel processing
        self.max_workers = max_workers

    def run_all_strategies(self, df, append=True, ta_indicator_value=False, 
                           signal_score=True, signal_value=False, signal_explanation=False):
        """
        Runs the `run_all_strategies` method for each strategy instance using the provided DataFrame in parallel.
        The results are stored as attributes (e.g., AberrationStrategies_df) and then concatenated
        horizontally into one DataFrame.
        """
        results = {}
        
        logger.info(f"Running {len(self.strategy_instances)} strategies in parallel with {self.max_workers} workers")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all strategy tasks
            future_to_strategy = {
                executor.submit(
                    _run_single_strategy, 
                    (name, instance), 
                    df, append, ta_indicator_value, signal_score, signal_value, signal_explanation
                ): name for name, instance in self.strategy_instances.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy):
                try:
                    name, result_df = future.result()
                    results[name] = result_df
                    setattr(self, f"{name}_df", result_df)
                    logger.debug(f"Completed strategy: {name}")
                except Exception as e:
                    strategy_name = future_to_strategy[future]
                    logger.error(f"Strategy {strategy_name} generated an exception: {e}")
                    results[strategy_name] = pd.DataFrame()
                    setattr(self, f"{strategy_name}_df", pd.DataFrame())
        
        logger.info(f"Completed all {len(results)} strategies")
        
        # Filter out empty DataFrames before concatenation
        valid_results = [df for df in results.values() if not df.empty]
        
        if valid_results:
            return pd.concat(valid_results, axis=1)
        else:
            logger.warning("No valid strategy results to concatenate")
            return pd.DataFrame()

class AllTrendStrategies:
    def __init__(self, max_workers=4):
        # List all strategy classes (assumed imported/defined elsewhere)
        trend_strategies = [
            AdaptivePriceZoneStrategies,
            AllMovingAverageStrategies,
            ArcherMovingAveragesTrendsStrategies,
            ArnaudLegouxMovingAverageStrategies,
            AroonStrategies,
            AroonOscillatorStrategies,
            AverageDirectionalIndexStrategies,
            AveragePriceStrategies,
            BiasStrategies,
            CorrelationTrendIndicatorStrategies,
            CrossSignalsStrategies,
            DecayStrategies,
            DecreasingPriceStrategies,
            DirectionalMovementStrategies,
            DonchianChannelStrategies,
            DoubleExponentialMovingAverageStrategies,
            EhlersSuperSmootherFilterStrategies,
            ElderRayIndexStrategies,
            ExponentialMovingAverageStrategies,
            FibonacciPivotPointsStrategies,
            FibonacciWeightedMovingAverageStrategies,
            FractalAdaptiveMovingAverageStrategies,
            GannHighLowActivatorStrategies,
            HighLowAverageStrategies,
            HilbertTransformDominantCyclePeriodStrategies,
            HilbertTransformDominantCyclePhaseStrategies,
            HilbertTransformInstantaneousTrendlineStrategies,
            HilbertTransformPhasorComponentsStrategies,
            HilbertTransformSineWaveStrategies,
            HilbertTransformTrendCycleStrategies,
            HoltWinterChannelStrategies,
            HoltWinterMovingAverageStrategies,
            HullExponentialMovingAverageStrategies,
            HullMovingAverageStrategies,
            IchimokuCloudStrategies,
            IncreasingPriceStrategies,
            JurikMovingAverageStrategies,
            KaufmanAdaptiveMovingAverageStrategies,
            KaufmanEfficiencyIndicatorStrategies,
            LinearRegressionStrategies,
            LinearRegressionAngleStrategies,
            LinearRegressionInterceptStrategies,
            LinearRegressionSlopeStrategies,
            LongRunStrategies,
            McGinleyDynamicStrategies,
            MedianPriceStrategies,
            MidPointOverPeriodStrategies,
            MidpointPricePeriodStrategies,
            MinusDirectionalIndicatorStrategies,
            MinusDirectionalMovementStrategies,
            OHLC_AverageStrategies,
            ParabolicStopAndReverseStrategies,
            PascalsWeightedMovingAverageStrategies,
            PivotPointsStrategies,
            PlusDirectionalIndicatorStrategies,
            PlusDirectionalMovementStrategies,
            QStickStrategies,
            ShortRunStrategies,
            SineWeightedMovingAverageStrategies,
            SlopeStrategies,
            SmoothedExponentialMovingAverageStrategies,
            SmoothedSimpleMovingAverageStrategies,
            StopAndReverseStrategies,
            SummationStrategies,
            SupertrendStrategies,
            SymmetricWeightedMovingAverageStrategies,
            T3MovingAverageStrategies,
            TrendSignalsStrategies,
            TriangularMovingAverageStrategies,
            TTMTrendStrategies,
            TypicalPriceStrategies,
            VariableIndexDynamicAverageStrategies,
            VerticalHorizontalFilterStrategies,
            VortexIndicatorStrategies,
            WeightedClosingPriceStrategies,
            WeightedMovingAverageStrategies,
            WildersMovingAverageStrategies,
            ZeroLagExponentialMovingAverageStrategies,
            ZeroLagSimpleMovingAverageStrategies,
        ]
        # Instantiate each strategy and store the instance in a dictionary
        self.strategy_instances = {}
        for cls in trend_strategies:
            self.strategy_instances[cls.__name__] = cls()
        
        # Set max_workers for parallel processing
        self.max_workers = max_workers

    def run_all_strategies(self, df, append=True, ta_indicator_value=False, 
                           signal_score=True, signal_value=False, signal_explanation=False):
        """
        Runs the `run_all_strategies` method for each strategy instance using the provided DataFrame in parallel.
        The results are stored as attributes (e.g., AberrationStrategies_df) and then concatenated
        horizontally into one DataFrame.
        """
        results = {}
        
        logger.info(f"Running {len(self.strategy_instances)} trend strategies in parallel with {self.max_workers} workers")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all strategy tasks
            future_to_strategy = {
                executor.submit(
                    _run_single_strategy, 
                    (name, instance), 
                    df, append, ta_indicator_value, signal_score, signal_value, signal_explanation
                ): name for name, instance in self.strategy_instances.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy):
                try:
                    name, result_df = future.result()
                    results[name] = result_df
                    setattr(self, f"{name}_df", result_df)
                    logger.debug(f"Completed trend strategy: {name}")
                except Exception as e:
                    strategy_name = future_to_strategy[future]
                    logger.error(f"Trend strategy {strategy_name} generated an exception: {e}")
                    results[strategy_name] = pd.DataFrame()
                    setattr(self, f"{strategy_name}_df", pd.DataFrame())
        
        logger.info(f"Completed all {len(results)} trend strategies")
        
        # Filter out empty DataFrames before concatenation
        valid_results = [df for df in results.values() if not df.empty]
        
        if valid_results:
            return pd.concat(valid_results, axis=1)
        else:
            logger.warning("No valid trend strategy results to concatenate")
            return pd.DataFrame()

class AllMomentumStrategies:
    def __init__(self, max_workers=4):
        # List all strategy classes (assumed imported/defined elsewhere)
        momentum_strategies = [
            AbsolutePriceOscillatorStrategies,
            AwesomeOscillatorStrategies,
            BalanceOfPowerStrategies,
            BRARStrategies,
            BuyAndSellPressureStrategies,
            CenterOfGravityStrategies,
            ChandeForecastOscillatorStrategies,
            ChandeMomentumOscillatorStrategies,
            CommodityChannelIndexStrategies,
            CoppockCurveStrategies,
            CumulativeForceIndexStrategies,
            DetrendedPriceOscillatorStrategies,
            InertiaStrategies,
            InverseFisherTransformRSIStrategies,
            KDJIndicatorStrategies,
            KnowSureThingStrategies,
            MarkWhistlersWAVEPMStrategies,
            MarketMomentumStrategies,
            MomentumStrategies,
            MomentumBreakoutBandsStrategies,
            MACDStrategies,
            PercentagePriceOscillatorStrategies,
            PrettyGoodOscillatorStrategies,
            PsychologicalLineStrategies,
            QuantitativeQualitativeEstimationStrategies,
            RateOfChangeStrategies,
            RelativeStrengthIndexStrategies,
            RelativeStrengthXtraStrategies,
            RelativeVigorIndexStrategies,
            SchaffTrendCycleStrategies,
            SmiErgodicOscillatorStrategies,
            StochasticStrategies,
            StochasticFastStrategies,
            StochasticOscillatorStrategies,
            StochasticOscillatorKStrategies,
            StochasticRSIStrategies,
            StochasticOscillatorDStrategies,
            TDSequentialStrategies,
            TripleExponentialMovingAverageOscillatorStrategies,
            TrixStrategies,
            TwiggsMoneyIndexStrategies,
            UltimateOscillatorStrategies,
            UpDownStrategies,
            WaveTrendOscillatorStrategies,
            WilliamsRStrategies,
        ]
        # Instantiate each strategy and store the instance in a dictionary
        self.strategy_instances = {}
        for cls in momentum_strategies:
            self.strategy_instances[cls.__name__] = cls()
        
        # Set max_workers for parallel processing
        self.max_workers = max_workers

    def run_all_strategies(self, df, append=True, ta_indicator_value=False, 
                           signal_score=True, signal_value=False, signal_explanation=False):
        """
        Runs the `run_all_strategies` method for each strategy instance using the provided DataFrame in parallel.
        The results are stored as attributes (e.g., AberrationStrategies_df) and then concatenated
        horizontally into one DataFrame.
        """
        results = {}
        
        logger.info(f"Running {len(self.strategy_instances)} momentum strategies in parallel with {self.max_workers} workers")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all strategy tasks
            future_to_strategy = {
                executor.submit(
                    _run_single_strategy, 
                    (name, instance), 
                    df, append, ta_indicator_value, signal_score, signal_value, signal_explanation
                ): name for name, instance in self.strategy_instances.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy):
                try:
                    name, result_df = future.result()
                    results[name] = result_df
                    setattr(self, f"{name}_df", result_df)
                    logger.debug(f"Completed momentum strategy: {name}")
                except Exception as e:
                    strategy_name = future_to_strategy[future]
                    logger.error(f"Momentum strategy {strategy_name} generated an exception: {e}")
                    results[strategy_name] = pd.DataFrame()
                    setattr(self, f"{strategy_name}_df", pd.DataFrame())
        
        logger.info(f"Completed all {len(results)} momentum strategies")
        
        # Filter out empty DataFrames before concatenation
        valid_results = [df for df in results.values() if not df.empty]
        
        if valid_results:
            return pd.concat(valid_results, axis=1)
        else:
            logger.warning("No valid momentum strategy results to concatenate")
            return pd.DataFrame()

class AllVolatilityStrategies:
    def __init__(self, max_workers=4):
        # List all strategy classes (assumed imported/defined elsewhere)
        volatility_strategies = [
            AccelerationBandsStrategies,
            AverageTrueRangeStrategies,
            ChandeKrollStopStrategies,
            ChandelierExitStrategies,
            BollingerBandsStrategies,
            BollingerBandsWidthStrategies,
            ChoppinessIndexStrategies,
            KeltnerChannelStrategies,
            MassIndexStrategies,
            MovingStandardDeviationStrategies,
            NormalizedAverageTrueRangeStrategies,
            NormalizedBASPStrategies,
            PercentBStrategies,
            RelativeVolatilityIndexStrategies,
            SqueezeStrategies,
            SqueezeProStrategies,
            StandardDeviationStrategies,
            UlcerIndexStrategies,
            VarianceStrategies,
            PriceDistanceStrategies,
        ]
        # Instantiate each strategy and store the instance in a dictionary
        self.strategy_instances = {}
        for cls in volatility_strategies:
            self.strategy_instances[cls.__name__] = cls()
        
        # Set max_workers for parallel processing
        self.max_workers = max_workers

    def run_all_strategies(self, df, append=True, ta_indicator_value=False, 
                           signal_score=True, signal_value=False, signal_explanation=False):
        """
        Runs the `run_all_strategies` method for each strategy instance using the provided DataFrame in parallel.
        The results are stored as attributes (e.g., AberrationStrategies_df) and then concatenated
        horizontally into one DataFrame.
        """
        results = {}
        
        logger.info(f"Running {len(self.strategy_instances)} volatility strategies in parallel with {self.max_workers} workers")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all strategy tasks
            future_to_strategy = {
                executor.submit(
                    _run_single_strategy, 
                    (name, instance), 
                    df, append, ta_indicator_value, signal_score, signal_value, signal_explanation
                ): name for name, instance in self.strategy_instances.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy):
                try:
                    name, result_df = future.result()
                    results[name] = result_df
                    setattr(self, f"{name}_df", result_df)
                    logger.debug(f"Completed volatility strategy: {name}")
                except Exception as e:
                    strategy_name = future_to_strategy[future]
                    logger.error(f"Volatility strategy {strategy_name} generated an exception: {e}")
                    results[strategy_name] = pd.DataFrame()
                    setattr(self, f"{strategy_name}_df", pd.DataFrame())
        
        logger.info(f"Completed all {len(results)} volatility strategies")
        
        # Filter out empty DataFrames before concatenation
        valid_results = [df for df in results.values() if not df.empty]
        
        if valid_results:
            return pd.concat(valid_results, axis=1)
        else:
            logger.warning("No valid volatility strategy results to concatenate")
            return pd.DataFrame()

class AllVolumeStrategies:
    def __init__(self, max_workers=4):
        # List all strategy classes (assumed imported/defined elsewhere)
        volume_strategies = [
            AccumulationDistributionLineStrategies,
            AccumulationDistributionIndexStrategies,
            AccumulationDistributionOscillatorStrategies,
            ArcherOnBalanceVolumeStrategies,
            ChaikinADLineStrategies,
            ChaikinADOscillatorStrategies,
            ChaikinMoneyFlowStrategies,
            ChaikinOscillatorStrategies,
            ElasticVolumeMovingAverageStrategies,
            ElasticVolumeMACDStrategies,
            FiniteVolumeElementStrategies,
            KlingerVolumeOscillatorStrategies,
            MoneyFlowIndexStrategies,
            NegativeVolumeIndexStrategies,
            OnBalanceVolumeStrategies,
            PercentageVolumeOscillatorStrategies,
            PositiveVolumeIndexStrategies,
            PriceVolumeRankStrategies,
            PriceVolumeTrendStrategies,
            PriceVolumeStrategies,
            VolumeAdjustedMovingAverageStrategies,
            VolumeFlowIndicatorStrategies,
            VolumePriceTrendStrategies,
            VolumeWeightedAveragePriceStrategies,
            VolumeWeightedMovingAverageStrategies,
            VolumeWeightedMACDStrategies,
            WeightedOnBalanceVolumeStrategies,
        ]
        # Instantiate each strategy and store the instance in a dictionary
        self.strategy_instances = {}
        for cls in volume_strategies:
            self.strategy_instances[cls.__name__] = cls()
        
        # Set max_workers for parallel processing
        self.max_workers = max_workers

    def run_all_strategies(self, df, append=True, ta_indicator_value=False, 
                           signal_score=True, signal_value=False, signal_explanation=False):
        """
        Runs the `run_all_strategies` method for each strategy instance using the provided DataFrame in parallel.
        The results are stored as attributes (e.g., AberrationStrategies_df) and then concatenated
        horizontally into one DataFrame.
        """
        results = {}
        
        logger.info(f"Running {len(self.strategy_instances)} volume strategies in parallel with {self.max_workers} workers")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all strategy tasks
            future_to_strategy = {
                executor.submit(
                    _run_single_strategy, 
                    (name, instance), 
                    df, append, ta_indicator_value, signal_score, signal_value, signal_explanation
                ): name for name, instance in self.strategy_instances.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_strategy):
                try:
                    name, result_df = future.result()
                    results[name] = result_df
                    setattr(self, f"{name}_df", result_df)
                    logger.debug(f"Completed volume strategy: {name}")
                except Exception as e:
                    strategy_name = future_to_strategy[future]
                    logger.error(f"Volume strategy {strategy_name} generated an exception: {e}")
                    results[strategy_name] = pd.DataFrame()
                    setattr(self, f"{strategy_name}_df", pd.DataFrame())
        
        logger.info(f"Completed all {len(results)} volume strategies")
        
        # Filter out empty DataFrames before concatenation
        valid_results = [df for df in results.values() if not df.empty]
        
        if valid_results:
            return pd.concat(valid_results, axis=1)
        else:
            logger.warning("No valid volume strategy results to concatenate")
            return pd.DataFrame()