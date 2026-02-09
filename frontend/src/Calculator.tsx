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
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-900 rounded-2xl mb-4 shadow-lg">
            <span className="text-3xl">🏠</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            SDA Price Calculator
          </h1>
          <p className="text-lg text-gray-600">
            Calculate NDIS Specialist Disability Accommodation pricing
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-2xl shadow-sm p-8 mb-6">
          <div className="flex items-center justify-between max-w-3xl mx-auto">
            {[
              { num: 1, label: 'Property' },
              { num: 2, label: 'Features' },
              { num: 3, label: 'Location' }
            ].map((step, idx) => (
              <div key={step.num} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                      currentStep >= step.num
                        ? 'bg-gradient-to-br from-purple-900 to-purple-700 text-white shadow-lg scale-110'
                        : 'bg-gray-100 text-gray-400'
                    }`}
                  >
                    {currentStep > step.num ? '✓' : step.num}
                  </div>
                  <span className={`mt-2 text-sm font-medium ${
                    currentStep >= step.num ? 'text-purple-900' : 'text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                </div>
                {idx < 2 && (
                  <div className={`h-1 flex-1 mx-4 transition-all duration-300 rounded ${
                    currentStep > step.num ? 'bg-gradient-to-r from-purple-900 to-purple-700' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Stock & Building Type */}
        <div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 p-8 mb-6">
          <div className="flex items-center mb-6">
            <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center mr-3">
              <span className="text-xl">🏢</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Step 1: Property Type
            </h2>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Dwelling Enrolled As
              </label>
              <select
                value={stockType}
                onChange={(e) => setStockType(e.target.value as StockType)}
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
              >
                <option value="POST_2023">Post-2023 New Build</option>
                <option value="PRE_2023">Pre-2023 New Build</option>
                <option value="EXISTING">Existing Stock</option>
                <option value="LEGACY">Legacy Stock</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Building Type
              </label>
              <select
                value={buildingType}
                onChange={(e) => setBuildingType(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
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
                className="w-full bg-gradient-to-r from-purple-900 to-purple-700 text-white py-4 px-6 rounded-xl hover:from-purple-800 hover:to-purple-600 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                Continue to Design Features →
              </button>
            )}
          </div>
        </div>

        {/* Step 2: Design Features */}
        {currentStep >= 2 && (
          <div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 p-8 mb-6 animate-fadeIn">
            <div className="flex items-center mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center mr-3">
                <span className="text-xl">⭐</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                Step 2: Design Features
              </h2>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Design Category
                </label>
                <select
                  value={designCategory}
                  onChange={(e) => {
                    setDesignCategory(e.target.value as DesignCategory);
                    const newCategory = designCategories.find(dc => dc.code === e.target.value);
                    if (newCategory && !newCategory.ooa_available.includes(ooaStatus)) {
                      setOOAStatus('NO_OOA');
                    }
                  }}
                  className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
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
                <div className="space-y-6 animate-fadeIn">
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-5 rounded-xl">
                    <label className="block text-sm font-semibold text-gray-700 mb-4">
                      On-site Overnight Assistance (OOA)
                    </label>
                    <div className="flex gap-4">
                      <label className="flex-1 flex items-center justify-center p-4 rounded-lg border-2 cursor-pointer transition-all hover:border-purple-300 bg-white"
                        style={{
                          borderColor: ooaStatus === 'NO_OOA' ? '#6A2875' : '#e5e7eb',
                          backgroundColor: ooaStatus === 'NO_OOA' ? '#faf5ff' : 'white'
                        }}>
                        <input
                          type="radio"
                          checked={ooaStatus === 'NO_OOA'}
                          onChange={() => setOOAStatus('NO_OOA')}
                          className="mr-3 w-5 h-5 text-purple-900"
                        />
                        <span className="font-medium">Without OOA</span>
                      </label>
                      <label className={`flex-1 flex items-center justify-center p-4 rounded-lg border-2 transition-all bg-white ${
                        canSelectWithOOA ? 'cursor-pointer hover:border-purple-300' : 'opacity-50 cursor-not-allowed'
                      }`}
                        style={{
                          borderColor: ooaStatus === 'WITH_OOA' ? '#6A2875' : '#e5e7eb',
                          backgroundColor: ooaStatus === 'WITH_OOA' ? '#faf5ff' : 'white'
                        }}>
                        <input
                          type="radio"
                          checked={ooaStatus === 'WITH_OOA'}
                          onChange={() => setOOAStatus('WITH_OOA')}
                          disabled={!canSelectWithOOA}
                          className="mr-3 w-5 h-5 text-purple-900"
                        />
                        <span className="font-medium">With OOA</span>
                      </label>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <label className="flex-1 flex items-center p-4 rounded-xl bg-gray-50 hover:bg-gray-100 cursor-pointer transition-all border-2 border-transparent hover:border-purple-200">
                      <input
                        type="checkbox"
                        checked={fireSprinklers}
                        onChange={(e) => setFireSprinklers(e.target.checked)}
                        className="mr-3 w-5 h-5 text-purple-900 rounded"
                      />
                      <span className="font-medium text-gray-700">🔥 Fire Sprinklers</span>
                    </label>

                    {stockType === 'POST_2023' && (
                      <label className="flex-1 flex items-center p-4 rounded-xl bg-gray-50 hover:bg-gray-100 cursor-pointer transition-all border-2 border-transparent hover:border-purple-200">
                        <input
                          type="checkbox"
                          checked={itcClaimed}
                          onChange={(e) => setItcClaimed(e.target.checked)}
                          className="mr-3 w-5 h-5 text-purple-900 rounded"
                        />
                        <span className="font-medium text-gray-700">💰 GST/ITC Claimed</span>
                      </label>
                    )}
                  </div>

                  {canProceedToStep3 && (
                    <button
                      onClick={() => setCurrentStep(3)}
                      className="w-full bg-gradient-to-r from-purple-900 to-purple-700 text-white py-4 px-6 rounded-xl hover:from-purple-800 hover:to-purple-600 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                    >
                      Continue to Location →
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Location */}
        {currentStep >= 3 && (
          <div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-shadow duration-300 p-8 mb-6 animate-fadeIn">
            <div className="flex items-center mb-6">
              <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center mr-3">
                <span className="text-xl">📍</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                Step 3: Location
              </h2>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  SA4 Region
                </label>
                <select
                  value={sa4Region}
                  onChange={(e) => setSa4Region(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all"
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
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 animate-shake">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">⚠️</span>
                    <p className="text-red-800 text-sm font-medium">{error}</p>
                  </div>
                </div>
              )}

              <button
                onClick={handleCalculate}
                disabled={!canCalculate || loading}
                className="w-full bg-gradient-to-r from-purple-900 to-purple-700 text-white py-5 px-6 rounded-xl hover:from-purple-800 hover:to-purple-600 transition-all duration-300 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed font-bold text-xl shadow-xl hover:shadow-2xl transform hover:-translate-y-1 disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-6 w-6 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Calculating...
                  </span>
                ) : (
                  '🎯 Calculate SDA Pricing'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {result && currentStep === 4 && (
          <div className="animate-fadeIn">
            {/* Main Result - Hero */}
            <div className="bg-gradient-to-br from-purple-900 via-purple-800 to-purple-700 rounded-3xl shadow-2xl p-10 mb-6 text-white">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-6">
                  <span className="text-5xl">💎</span>
                </div>
                <p className="text-lg font-medium mb-3 opacity-90">Annual SDA Amount</p>
                <p className="text-6xl font-bold mb-2">
                  {formatCurrency(Number(result.annual_sda_amount))}
                </p>
                <p className="text-purple-200 text-sm">per year</p>
              </div>
            </div>

            {/* Calculation Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mr-3">
                    <span className="text-2xl">💵</span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Base Price</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(Number(result.base_price))}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center mr-3">
                    <span className="text-2xl">📊</span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Location Factor</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {Number(result.location_factor).toFixed(4)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* MRRC Section */}
            <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mr-3">
                  <span className="text-2xl">🏡</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Maximum Reasonable Rent Contribution (MRRC)
                </h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Single */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
                  <div className="flex items-center mb-4">
                    <span className="text-3xl mr-3">👤</span>
                    <p className="text-lg font-bold text-gray-900">Single Occupancy</p>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Fortnightly</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(Number(result.mrrc.single.fortnightly))}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Annual</p>
                      <p className="text-xl font-semibold text-gray-700">
                        {formatCurrency(Number(result.mrrc.single.annual))}
                      </p>
                    </div>
                    <div className="pt-3 border-t-2 border-blue-300">
                      <p className="text-sm text-gray-600 mb-1">Net NDIA Payment</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {formatCurrency(Number(result.net_ndia_single))}
                      </p>
                      <p className="text-xs text-gray-500">per year</p>
                    </div>
                  </div>
                </div>

                {/* Couple */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border-2 border-purple-200">
                  <div className="flex items-center mb-4">
                    <span className="text-3xl mr-3">👥</span>
                    <p className="text-lg font-bold text-gray-900">Couple Occupancy</p>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Fortnightly</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatCurrency(Number(result.mrrc.couple.fortnightly))}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Annual</p>
                      <p className="text-xl font-semibold text-gray-700">
                        {formatCurrency(Number(result.mrrc.couple.annual))}
                      </p>
                    </div>
                    <div className="pt-3 border-t-2 border-purple-300">
                      <p className="text-sm text-gray-600 mb-1">Net NDIA Payment</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {formatCurrency(Number(result.net_ndia_couple))}
                      </p>
                      <p className="text-xs text-gray-500">per year</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Summary Card */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-6 mb-6 border border-gray-200">
              <h4 className="font-bold text-gray-900 mb-4 flex items-center">
                <span className="text-xl mr-2">📋</span>
                Calculation Summary
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Stock Type:</span>
                  <span className="ml-2 font-semibold text-gray-900">{stockType.replace('_', ' ')}</span>
                </div>
                <div>
                  <span className="text-gray-600">Building:</span>
                  <span className="ml-2 font-semibold text-gray-900">{buildingType}</span>
                </div>
                <div>
                  <span className="text-gray-600">Design:</span>
                  <span className="ml-2 font-semibold text-gray-900">
                    {designCategory && designCategoryNames[designCategory]} ({ooaStatus === 'WITH_OOA' ? 'With OOA' : 'Without OOA'})
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Location:</span>
                  <span className="ml-2 font-semibold text-gray-900">{sa4Region}</span>
                </div>
                <div>
                  <span className="text-gray-600">Effective Date:</span>
                  <span className="ml-2 font-semibold text-gray-900">{result.effective_date}</span>
                </div>
              </div>
            </div>

            {/* Calculate Again Button */}
            <button
              onClick={() => {
                setResult(null);
                setCurrentStep(1);
                setStockType('POST_2023');
                setBuildingType('');
                setDesignCategory('');
                setSa4Region('');
              }}
              className="w-full bg-white text-purple-900 border-2 border-purple-900 py-4 px-6 rounded-xl hover:bg-purple-50 transition-all duration-300 font-semibold text-lg shadow-md hover:shadow-lg"
            >
              ↻ Calculate Again
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
        
        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
}
