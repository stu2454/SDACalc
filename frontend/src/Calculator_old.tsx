import { useState, useEffect } from 'react';
import { api } from './api';
import type {
  StockType,
  DesignCategory,
  OOAStatus,
  CalculationResponse,
  BuildingTypeOption,
  DesignCategoryOption,
  SA4RegionOption,
  ErrorResponse,
} from './types';

export default function Calculator() {
  // Form state
  const [stockType, setStockType] = useState<StockType>('POST_2023');
  const [buildingType, setBuildingType] = useState('');
  const [designCategory, setDesignCategory] = useState<DesignCategory | ''>('');
  const [ooaStatus, setOOAStatus] = useState<OOAStatus>('NO_OOA');
  const [fireSprinklers, setFireSprinklers] = useState(false);
  const [itcClaimed, setItcClaimed] = useState(true);
  const [sa4Region, setSa4Region] = useState('');

  // Options state
  const [buildingTypes, setBuildingTypes] = useState<BuildingTypeOption[]>([]);
  const [designCategories, setDesignCategories] = useState<DesignCategoryOption[]>([]);
  const [regions, setRegions] = useState<SA4RegionOption[]>([]);

  // UI state
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CalculationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadRegions();
  }, []);

  // Load building types when stock type changes
  useEffect(() => {
    loadBuildingTypes();
    setBuildingType('');
    setDesignCategory('');
  }, [stockType]);

  // Load design categories when building type changes
  useEffect(() => {
    if (buildingType) {
      loadDesignCategories();
      setDesignCategory('');
    }
  }, [stockType, buildingType]);

  const loadBuildingTypes = async () => {
    try {
      const types = await api.getBuildingTypes(stockType);
      setBuildingTypes(types);
    } catch (err) {
      console.error('Failed to load building types:', err);
    }
  };

  const loadDesignCategories = async () => {
    try {
      const options = await api.getOptions({ stock_type: stockType, building_type: buildingType });
      setDesignCategories(options.design_categories || []);
    } catch (err) {
      console.error('Failed to load design categories:', err);
    }
  };

  const loadRegions = async () => {
    try {
      const regionList = await api.getRegions();
      setRegions(regionList);
    } catch (err) {
      console.error('Failed to load regions:', err);
    }
  };

  const handleCalculate = async () => {
    if (!designCategory) return;

    setLoading(true);
    setError(null);

    try {
      const request = {
        stock_type: stockType,
        building_type: buildingType,
        design_category: designCategory,
        ooa_status: ooaStatus,
        fire_sprinklers: fireSprinklers,
        itc_claimed: stockType === 'POST_2023' ? itcClaimed : null,
        sa4_region: sa4Region,
      };

      const response = await api.calculate(request);
      setResult(response);
      setCurrentStep(4);
    } catch (err: any) {
      const errorData = err.response?.data as ErrorResponse;
      if (errorData?.errors) {
        setError(errorData.errors.map(e => e.message).join('; '));
      } else {
        setError(errorData?.detail || 'Calculation failed. Please check your inputs.');
      }
    } finally {
      setLoading(false);
    }
  };

  const canProceedToStep2 = stockType && buildingType;
  const canProceedToStep3 = canProceedToStep2 && designCategory;
  const canCalculate = canProceedToStep3 && sa4Region;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 2,
    }).format(value);
  };

  const designCategoryNames: Record<string, string> = {
    BASIC: 'Basic',
    IL: 'Improved Liveability',
    FA: 'Fully Accessible',
    ROBUST: 'Robust',
    ROBUST_BO: 'Robust with Breakout Room',
    HPS: 'High Physical Support',
  };

  const selectedDesignCategory = designCategories.find(dc => dc.code === designCategory);
  const canSelectWithOOA = selectedDesignCategory?.ooa_available.includes('WITH_OOA') ?? false;

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-purple-900 mb-2">
            SDA Price Calculator
          </h1>
          <p className="text-gray-600">
            Calculate NDIS Specialist Disability Accommodation pricing
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                    currentStep >= step
                      ? 'bg-purple-900 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step}
                </div>
                {step < 3 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      currentStep > step ? 'bg-purple-900' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Stock & Building Type */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Step 1: Stock and Building Type
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dwelling Enrolled As
              </label>
              <select
                value={stockType}
                onChange={(e) => setStockType(e.target.value as StockType)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="POST_2023">Post-2023 New Build</option>
                <option value="PRE_2023">Pre-2023 New Build</option>
                <option value="EXISTING">Existing Stock</option>
                <option value="LEGACY">Legacy Stock</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Building Type
              </label>
              <select
                value={buildingType}
                onChange={(e) => setBuildingType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Select building type...</option>
                {buildingTypes.map((bt) => (
                  <option key={bt.name} value={bt.name}>
                    {bt.name}
                  </option>
                ))}
              </select>
            </div>

            {canProceedToStep2 && (
              <button
                onClick={() => setCurrentStep(2)}
                className="w-full bg-purple-900 text-white py-2 px-4 rounded-lg hover:bg-purple-800 transition-colors"
              >
                Continue to Design Features
              </button>
            )}
          </div>
        </div>

        {/* Step 2: Design Features */}
        {currentStep >= 2 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Step 2: Design Features
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Design Category
                </label>
                <select
                  value={designCategory}
                  onChange={(e) => {
                    setDesignCategory(e.target.value as DesignCategory);
                    // Reset OOA if not available for new category
                    const newCategory = designCategories.find(dc => dc.code === e.target.value);
                    if (newCategory && !newCategory.ooa_available.includes(ooaStatus)) {
                      setOOAStatus('NO_OOA');
                    }
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select design category...</option>
                  {designCategories.map((dc) => (
                    <option key={dc.code} value={dc.code}>
                      {dc.name}
                    </option>
                  ))}
                </select>
              </div>

              {designCategory && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      On-site Overnight Assistance (OOA)
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          checked={ooaStatus === 'NO_OOA'}
                          onChange={() => setOOAStatus('NO_OOA')}
                          className="mr-2"
                        />
                        <span>Without OOA</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          checked={ooaStatus === 'WITH_OOA'}
                          onChange={() => setOOAStatus('WITH_OOA')}
                          disabled={!canSelectWithOOA}
                          className="mr-2"
                        />
                        <span className={!canSelectWithOOA ? 'text-gray-400' : ''}>
                          With OOA
                        </span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={fireSprinklers}
                        onChange={(e) => setFireSprinklers(e.target.checked)}
                        className="mr-2"
                      />
                      <span className="text-sm font-medium text-gray-700">Fire Sprinklers</span>
                    </label>
                  </div>

                  {stockType === 'POST_2023' && (
                    <div>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={itcClaimed}
                          onChange={(e) => setItcClaimed(e.target.checked)}
                          className="mr-2"
                        />
                        <span className="text-sm font-medium text-gray-700">
                          GST Input Tax Credits Claimed
                        </span>
                      </label>
                    </div>
                  )}

                  {canProceedToStep3 && (
                    <button
                      onClick={() => setCurrentStep(3)}
                      className="w-full bg-purple-900 text-white py-2 px-4 rounded-lg hover:bg-purple-800 transition-colors"
                    >
                      Continue to Location
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Location */}
        {currentStep >= 3 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Step 3: Location
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SA4 Region
                </label>
                <select
                  value={sa4Region}
                  onChange={(e) => setSa4Region(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select region...</option>
                  {regions.map((region) => (
                    <option key={region.name} value={region.name}>
                      {region.name}
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <button
                onClick={handleCalculate}
                disabled={!canCalculate || loading}
                className="w-full bg-purple-900 text-white py-3 px-4 rounded-lg hover:bg-purple-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold"
              >
                {loading ? 'Calculating...' : 'Calculate SDA Pricing'}
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {result && currentStep === 4 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Results</h2>

            {/* Main Result */}
            <div className="bg-purple-50 rounded-lg p-6 mb-6">
              <p className="text-sm text-gray-600 mb-2">Annual SDA Amount</p>
              <p className="text-4xl font-bold text-purple-900">
                {formatCurrency(Number(result.annual_sda_amount))}
              </p>
            </div>

            {/* Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Base Price</p>
                <p className="text-xl font-semibold text-gray-900">
                  {formatCurrency(Number(result.base_price))}
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Location Factor</p>
                <p className="text-xl font-semibold text-gray-900">
                  {Number(result.location_factor).toFixed(4)}
                </p>
              </div>
            </div>

            {/* MRRC */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                Maximum Reasonable Rent Contribution (MRRC)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">Single Occupancy</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatCurrency(Number(result.mrrc.single.fortnightly))}/fortnight
                  </p>
                  <p className="text-sm text-gray-600">
                    ({formatCurrency(Number(result.mrrc.single.annual))}/year)
                  </p>
                  <div className="mt-2 pt-2 border-t border-blue-200">
                    <p className="text-xs text-gray-600">Net NDIA Payment</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(Number(result.net_ndia_single))}/year
                    </p>
                  </div>
                </div>
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-2">Couple Occupancy</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatCurrency(Number(result.mrrc.couple.fortnightly))}/fortnight
                  </p>
                  <p className="text-sm text-gray-600">
                    ({formatCurrency(Number(result.mrrc.couple.annual))}/year)
                  </p>
                  <div className="mt-2 pt-2 border-t border-blue-200">
                    <p className="text-xs text-gray-600">Net NDIA Payment</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(Number(result.net_ndia_couple))}/year
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
              <p className="mb-2">
                <strong>Stock Type:</strong> {stockType.replace('_', ' ')}
              </p>
              <p className="mb-2">
                <strong>Building:</strong> {buildingType}
              </p>
              <p className="mb-2">
                <strong>Design:</strong> {designCategory && designCategoryNames[designCategory]}{' '}
                ({ooaStatus === 'WITH_OOA' ? 'With OOA' : 'Without OOA'})
              </p>
              <p className="mb-2">
                <strong>Location:</strong> {sa4Region}
              </p>
              <p>
                <strong>Effective Date:</strong> {result.effective_date}
              </p>
            </div>

            <button
              onClick={() => {
                setResult(null);
                setCurrentStep(1);
              }}
              className="w-full mt-6 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Calculate Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
