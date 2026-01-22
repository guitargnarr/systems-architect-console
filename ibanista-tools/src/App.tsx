import { useState } from 'react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import type { Variants } from 'framer-motion';
import {
  Calculator,
  MapPin,
  Home,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  Sun,
  Mountain,
  Building2,
  Waves,
  Wine,
  Users,
  Plane,
  Heart,
  Briefcase,
  GraduationCap,
  TreePine,
  Mail,
  ExternalLink,
  PoundSterling,
  Euro,
  TrendingDown,
  Calendar,
  ChevronRight,
  Star,
  Phone,
  Shield,
  Clock,
  Banknote,
  Key,
  Zap,
  FileText
} from 'lucide-react';

// Types
interface CalculatorInputs {
  householdSize: string;
  currentRent: string;
  moveType: string;
  targetRegion: string;
}

interface QuizAnswer {
  questionId: number;
  answer: string;
}

interface Region {
  id: string;
  name: string;
  description: string;
  avgRent: number;
  climate: string;
  lifestyle: string;
  expatCommunity: string;
  image: string;
  scores: {
    urban: number;
    coastal: number;
    rural: number;
    wine: number;
    family: number;
    career: number;
  };
}

// Animation variants
const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
};

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
};

const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.5, ease: 'easeOut' } }
};

// Data - French Regions
const frenchRegions: Region[] = [
  {
    id: 'ile-de-france',
    name: 'Ile-de-France (Paris)',
    description: 'The heart of France with world-class culture, career opportunities, and urban sophistication.',
    avgRent: 1500,
    climate: 'Temperate oceanic',
    lifestyle: 'Urban cosmopolitan',
    expatCommunity: 'Very Large',
    image: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
    scores: { urban: 10, coastal: 1, rural: 2, wine: 5, family: 6, career: 10 }
  },
  {
    id: 'provence',
    name: 'Provence-Alpes-Cote d\'Azur',
    description: 'Sun-drenched Mediterranean living with stunning coastline, lavender fields, and relaxed pace.',
    avgRent: 1100,
    climate: 'Mediterranean',
    lifestyle: 'Relaxed coastal',
    expatCommunity: 'Large',
    image: 'https://images.unsplash.com/photo-1533104816931-20fa691ff6ca?w=800&q=80',
    scores: { urban: 6, coastal: 10, rural: 7, wine: 9, family: 7, career: 5 }
  },
  {
    id: 'nouvelle-aquitaine',
    name: 'Nouvelle-Aquitaine (Bordeaux)',
    description: 'Premier wine country with elegant architecture, Atlantic beaches, and exceptional quality of life.',
    avgRent: 850,
    climate: 'Oceanic',
    lifestyle: 'Wine & gastronomy',
    expatCommunity: 'Medium-Large',
    image: 'https://images.unsplash.com/photo-1565618754154-c8011e5df2a6?w=800&q=80',
    scores: { urban: 7, coastal: 8, rural: 8, wine: 10, family: 8, career: 6 }
  },
  {
    id: 'occitanie',
    name: 'Occitanie (Toulouse/Montpellier)',
    description: 'Dynamic region spanning Pyrenees to Mediterranean. Growing aerospace and tech hub.',
    avgRent: 750,
    climate: 'Mediterranean/Mountain',
    lifestyle: 'Dynamic & diverse',
    expatCommunity: 'Medium',
    image: 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=800&q=80',
    scores: { urban: 7, coastal: 7, rural: 9, wine: 7, family: 8, career: 7 }
  },
  {
    id: 'bretagne',
    name: 'Bretagne (Brittany)',
    description: 'Celtic heritage with dramatic coastlines, strong local culture, and affordable living.',
    avgRent: 650,
    climate: 'Oceanic',
    lifestyle: 'Coastal & cultural',
    expatCommunity: 'Medium',
    image: 'https://images.unsplash.com/photo-1560717799-0b7e6b0f5e26?w=800&q=80',
    scores: { urban: 5, coastal: 9, rural: 8, wine: 4, family: 9, career: 4 }
  },
  {
    id: 'auvergne',
    name: 'Auvergne-Rhone-Alpes (Lyon)',
    description: 'France\'s gastronomic capital with Alpine access, strong economy, and rich culture.',
    avgRent: 950,
    climate: 'Continental/Alpine',
    lifestyle: 'Urban & outdoors',
    expatCommunity: 'Large',
    image: 'https://images.unsplash.com/photo-1524397057410-1e775ed476f3?w=800&q=80',
    scores: { urban: 8, coastal: 1, rural: 6, wine: 8, family: 7, career: 8 }
  }
];

const quizQuestions = [
  {
    id: 1,
    question: 'What type of environment appeals to you most?',
    icon: MapPin,
    options: [
      { label: 'Vibrant city life', value: 'urban', icon: Building2 },
      { label: 'Coastal & beaches', value: 'coastal', icon: Waves },
      { label: 'Countryside tranquility', value: 'rural', icon: TreePine },
      { label: 'Mix of town and nature', value: 'mixed', icon: Mountain }
    ]
  },
  {
    id: 2,
    question: 'What climate do you prefer?',
    icon: Sun,
    options: [
      { label: 'Hot Mediterranean summers', value: 'mediterranean', icon: Sun },
      { label: 'Mild oceanic (like UK)', value: 'oceanic', icon: Waves },
      { label: 'Continental with seasons', value: 'continental', icon: TreePine },
      { label: 'Mountain climate', value: 'mountain', icon: Mountain }
    ]
  },
  {
    id: 3,
    question: 'What is your primary reason for relocating?',
    icon: Heart,
    options: [
      { label: 'Career opportunity', value: 'career', icon: Briefcase },
      { label: 'Retirement & lifestyle', value: 'retirement', icon: Sun },
      { label: 'Family & education', value: 'family', icon: GraduationCap },
      { label: 'Adventure & new experiences', value: 'adventure', icon: Plane }
    ]
  },
  {
    id: 4,
    question: 'How important is an established expat community?',
    icon: Users,
    options: [
      { label: 'Very important to me', value: 'high', icon: Users },
      { label: 'Somewhat important', value: 'medium', icon: Users },
      { label: 'Not particularly important', value: 'low', icon: Users },
      { label: 'I prefer full immersion', value: 'none', icon: Heart }
    ]
  },
  {
    id: 5,
    question: 'Which lifestyle element matters most to you?',
    icon: Wine,
    options: [
      { label: 'Food & wine culture', value: 'gastronomy', icon: Wine },
      { label: 'Outdoor activities', value: 'outdoor', icon: Mountain },
      { label: 'Arts & cultural scene', value: 'culture', icon: Building2 },
      { label: 'Peaceful daily rhythm', value: 'peaceful', icon: Home }
    ]
  }
];

// Services data from ibanista.com
const services = [
  {
    icon: Banknote,
    title: 'Money Transfers',
    description: 'Competitive rates and personal support for your international transfers.',
    cta: 'Learn More',
    link: 'https://www.ibanista.com/send-money-to-france/'
  },
  {
    icon: Key,
    title: 'Long-Term Rentals',
    description: 'Navigate the French rental market with expert guidance and full support.',
    cta: 'View Service',
    link: 'https://www.ibanista.com/find-long-term-rentals-in-france/'
  },
  {
    icon: Clock,
    title: 'Power Hour',
    description: '60-minute strategy session with Ben to plan your move with confidence.',
    cta: 'Book Session',
    link: 'https://www.ibanista.com/moving-to-france-power-hour-11-strategy-session-with-ben-small/'
  },
  {
    icon: Zap,
    title: 'Expat Care Package',
    description: 'Utilities, internet, and practical setup support for your new French home.',
    cta: 'Explore',
    link: 'https://www.ibanista.com/expat-care-package/'
  }
];

// Trust stats
const trustStats = [
  { value: '5,000+', label: 'Newsletter Subscribers' },
  { value: '50+', label: 'Five-Star Reviews' },
  { value: 'FCA', label: 'Regulated Partners' }
];

// Hero Section with parallax
function HeroSection() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 150]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <section className="relative min-h-[85vh] flex items-center overflow-hidden">
      {/* Background Image with Parallax */}
      <motion.div
        className="absolute inset-0 z-0"
        style={{ y }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-primary-900/95 via-primary-800/90 to-primary-900/80 z-10" />
        <img
          src="/hero-bordeaux.webp"
          alt="Place de la Bourse, Bordeaux - Miroir d'eau with tram"
          className="w-full h-full object-cover"
        />
      </motion.div>

      {/* Animated gradient orbs */}
      <div className="absolute inset-0 z-10 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-1/4 -right-1/4 w-1/2 h-1/2 bg-accent-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -bottom-1/4 -left-1/4 w-1/2 h-1/2 bg-primary-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 4 }}
        />
      </div>

      <motion.div
        className="relative z-20 max-w-6xl mx-auto px-4 py-20"
        style={{ opacity }}
      >
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="max-w-3xl"
        >
          <motion.div variants={fadeInUp} className="mb-6">
            <span className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 text-white/90 text-sm px-4 py-2 rounded-full">
              <span className="w-2 h-2 bg-accent-400 rounded-full animate-pulse" />
              UK to France Relocation Specialists
            </span>
          </motion.div>

          <motion.h1
            variants={fadeInUp}
            className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight"
          >
            Your move to France,{' '}
            <span className="text-accent-400">the calm, confident</span>{' '}
            version
          </motion.h1>

          <motion.p
            variants={fadeInUp}
            className="text-xl text-primary-100 mb-8 leading-relaxed max-w-2xl"
          >
            France is calling. But the process can feel overwhelming.
            We're here to make your relocation smooth, supported, and stress-free.
          </motion.p>

          <motion.div variants={fadeInUp} className="flex flex-wrap gap-4">
            <a
              href="#tools"
              className="btn-accent text-base px-8 py-4 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
            >
              Explore Free Tools <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="https://www.ibanista.com/contact"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white/10 backdrop-blur-sm border border-white/30 text-white font-medium px-8 py-4 rounded hover:bg-white/20 transition-all inline-flex items-center gap-2"
            >
              <Phone className="w-5 h-5" />
              Book Free Consultation
            </a>
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center pt-2">
          <div className="w-1.5 h-3 bg-white/50 rounded-full" />
        </div>
      </motion.div>
    </section>
  );
}

// Trust Badges Section
function TrustSection() {
  return (
    <section className="bg-white py-8 border-b border-primary-100">
      <div className="max-w-6xl mx-auto px-4">
        <motion.div
          className="flex flex-wrap justify-center items-center gap-8 md:gap-16"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          {trustStats.map((stat, index) => (
            <motion.div
              key={index}
              variants={scaleIn}
              className="text-center"
            >
              <div className="text-2xl md:text-3xl font-bold text-primary-800">{stat.value}</div>
              <div className="text-sm text-primary-500">{stat.label}</div>
            </motion.div>
          ))}
          <motion.div variants={scaleIn} className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-5 h-5 fill-accent-400 text-accent-400" />
            ))}
            <span className="ml-2 text-sm text-primary-500">Trustpilot</span>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

// Services Section
function ServicesSection() {
  return (
    <section className="py-20 bg-primary-50">
      <div className="max-w-6xl mx-auto px-4">
        <motion.div
          className="text-center mb-12"
          variants={fadeInUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-4xl font-bold text-primary-800 mb-4">
            How We Help You Move
          </h2>
          <p className="text-primary-600 text-lg max-w-2xl mx-auto">
            From finances to finding your home, we've got every step covered.
          </p>
        </motion.div>

        <motion.div
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <motion.a
                key={index}
                href={service.link}
                target="_blank"
                rel="noopener noreferrer"
                variants={fadeInUp}
                whileHover={{ y: -8, transition: { duration: 0.2 } }}
                className="bg-white rounded-xl p-6 shadow-soft hover:shadow-elevated transition-all group cursor-pointer"
              >
                <div className="w-14 h-14 bg-primary-100 group-hover:bg-primary-700 rounded-xl flex items-center justify-center mb-5 transition-colors duration-300">
                  <Icon className="w-7 h-7 text-primary-700 group-hover:text-white transition-colors duration-300" />
                </div>
                <h3 className="text-xl font-semibold text-primary-800 mb-2 group-hover:text-primary-700 transition-colors">
                  {service.title}
                </h3>
                <p className="text-primary-500 text-sm mb-4 leading-relaxed">
                  {service.description}
                </p>
                <span className="text-accent-600 font-medium text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
                  {service.cta} <ChevronRight className="w-4 h-4" />
                </span>
              </motion.a>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}

// Calculator Component
function RelocationCalculator() {
  const [inputs, setInputs] = useState<CalculatorInputs>({
    householdSize: '2',
    currentRent: '1500',
    moveType: 'full',
    targetRegion: 'provence'
  });
  const [showResults, setShowResults] = useState(false);

  const calculateCosts = () => {
    const household = parseInt(inputs.householdSize) || 2;
    const ukRent = parseInt(inputs.currentRent) || 1500;

    const movingCosts: Record<string, number> = {
      studio: 900,
      partial: 1200,
      full: 2000
    };
    const baseCost = movingCosts[inputs.moveType] || 1500;
    const totalMovingCost = baseCost * (1 + (household - 1) * 0.3);

    const region = frenchRegions.find(r => r.id === inputs.targetRegion) || frenchRegions[0];
    const franceRent = region.avgRent;
    const rentSavings = ukRent - franceRent;
    const monthlySavingsPercent = 0.32;
    const monthlyBudget = franceRent + (household * 400);

    return {
      movingCost: Math.round(totalMovingCost),
      monthlyBudget: Math.round(monthlyBudget),
      rentSavings: Math.round(rentSavings),
      annualSavings: Math.round(rentSavings * 12 + (ukRent * monthlySavingsPercent * 12)),
      region: region.name,
      regionImage: region.image,
      breakEven: totalMovingCost > 0 ? Math.ceil(totalMovingCost / (rentSavings > 0 ? rentSavings : 200)) : 0
    };
  };

  const results = calculateCosts();

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-elevated"
      >
        <div className="flex items-center gap-4 mb-8">
          <div className="w-14 h-14 bg-primary-100 rounded-lg flex items-center justify-center">
            <Calculator className="w-7 h-7 text-primary-700" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-primary-800">Relocation Budget Calculator</h2>
            <p className="text-primary-500">Estimate your UK to France move costs</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div>
            <label className="block text-sm font-medium text-primary-700 mb-2">
              Household Size
            </label>
            <select
              value={inputs.householdSize}
              onChange={(e) => setInputs({ ...inputs, householdSize: e.target.value })}
              className="select-field"
            >
              <option value="1">1 person</option>
              <option value="2">2 people</option>
              <option value="3">3 people</option>
              <option value="4">4+ people</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-primary-700 mb-2">
              Current UK Monthly Rent
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-primary-400">
                <PoundSterling className="w-4 h-4" />
              </span>
              <input
                type="number"
                value={inputs.currentRent}
                onChange={(e) => setInputs({ ...inputs, currentRent: e.target.value })}
                className="input-field pl-10"
                placeholder="1500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-primary-700 mb-2">
              Move Type
            </label>
            <select
              value={inputs.moveType}
              onChange={(e) => setInputs({ ...inputs, moveType: e.target.value })}
              className="select-field"
            >
              <option value="studio">Studio/Minimal (~£900)</option>
              <option value="partial">Partial household (~£1,200)</option>
              <option value="full">Full household (~£2,000+)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-primary-700 mb-2">
              Target Region in France
            </label>
            <select
              value={inputs.targetRegion}
              onChange={(e) => setInputs({ ...inputs, targetRegion: e.target.value })}
              className="select-field"
            >
              {frenchRegions.map(region => (
                <option key={region.id} value={region.id}>{region.name}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => setShowResults(true)}
          className="btn-primary w-full text-base"
        >
          Calculate My Budget <ArrowRight className="w-5 h-5" />
        </button>

        <AnimatePresence>
          {showResults && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-8 pt-8 border-t border-primary-100"
            >
              <h3 className="text-xl font-semibold text-primary-800 mb-6">Your Estimated Costs</h3>

              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 }}
                  className="bg-primary-50 rounded-lg p-5 border border-primary-100"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <PoundSterling className="w-4 h-4 text-primary-500" />
                    <p className="text-sm text-primary-600 font-medium">One-Time Moving Cost</p>
                  </div>
                  <p className="text-3xl font-bold text-primary-800">£{results.movingCost.toLocaleString()}</p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="bg-accent-50 rounded-lg p-5 border border-accent-100"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Euro className="w-4 h-4 text-accent-600" />
                    <p className="text-sm text-accent-700 font-medium">Monthly Budget in France</p>
                  </div>
                  <p className="text-3xl font-bold text-accent-700">€{results.monthlyBudget.toLocaleString()}</p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="bg-success-50 rounded-lg p-5 border border-success-100"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <TrendingDown className="w-4 h-4 text-success-600" />
                    <p className="text-sm text-success-700 font-medium">Monthly Rent Savings</p>
                  </div>
                  <p className="text-3xl font-bold text-success-700">£{results.rentSavings.toLocaleString()}</p>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 }}
                  className="bg-success-50 rounded-lg p-5 border border-success-100"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Calendar className="w-4 h-4 text-success-600" />
                    <p className="text-sm text-success-700 font-medium">Est. Annual Savings</p>
                  </div>
                  <p className="text-3xl font-bold text-success-700">£{results.annualSavings.toLocaleString()}</p>
                </motion.div>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-primary-50 rounded-lg p-5 border border-primary-100 mb-6"
              >
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-success-600" />
                  <p className="font-semibold text-primary-800">Break-even Timeline</p>
                </div>
                <p className="text-primary-600">
                  Your moving costs will be recovered in approximately <span className="font-semibold text-primary-800">{results.breakEven} months</span> through cost-of-living savings in {results.region}.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-primary-700 rounded-lg p-6 text-white"
              >
                <p className="font-semibold text-lg mb-2">Ready to take the next step?</p>
                <p className="text-primary-200 mb-4">
                  Get personalised guidance from Ibanista's UK-France relocation specialists.
                </p>
                <a
                  href="https://www.ibanista.com/contact"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 bg-white text-primary-700 px-5 py-2.5 rounded font-medium hover:bg-primary-50 transition-colors"
                >
                  Contact Ibanista <ExternalLink className="w-4 h-4" />
                </a>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

// Quiz Component
function RegionFinderQuiz() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [email, setEmail] = useState('');
  const [emailSubmitted, setEmailSubmitted] = useState(false);

  const handleAnswer = (answer: string) => {
    const newAnswers = [...answers, { questionId: quizQuestions[currentQuestion].id, answer }];
    setAnswers(newAnswers);

    if (currentQuestion < quizQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
    }
  };

  const calculateMatches = () => {
    const scores: Record<string, number> = {};

    frenchRegions.forEach(region => {
      let score = 0;

      answers.forEach(answer => {
        switch (answer.questionId) {
          case 1:
            if (answer.answer === 'urban') score += region.scores.urban;
            if (answer.answer === 'coastal') score += region.scores.coastal;
            if (answer.answer === 'rural') score += region.scores.rural;
            if (answer.answer === 'mixed') score += (region.scores.urban + region.scores.rural) / 2;
            break;
          case 2:
            if (answer.answer === 'mediterranean' && region.climate.includes('Mediterranean')) score += 10;
            if (answer.answer === 'oceanic' && region.climate.includes('Oceanic')) score += 10;
            if (answer.answer === 'continental' && region.climate.includes('Continental')) score += 10;
            if (answer.answer === 'mountain' && region.climate.includes('Alpine')) score += 10;
            break;
          case 3:
            if (answer.answer === 'career') score += region.scores.career;
            if (answer.answer === 'family') score += region.scores.family;
            if (answer.answer === 'retirement') score += (10 - region.scores.career) + region.scores.wine;
            if (answer.answer === 'adventure') score += 5;
            break;
          case 4:
            const expatScore = region.expatCommunity === 'Very Large' ? 10 : region.expatCommunity === 'Large' ? 8 : region.expatCommunity === 'Medium-Large' ? 6 : 4;
            if (answer.answer === 'high') score += expatScore;
            if (answer.answer === 'medium') score += expatScore * 0.5;
            if (answer.answer === 'none') score += (10 - expatScore);
            break;
          case 5:
            if (answer.answer === 'gastronomy') score += region.scores.wine;
            if (answer.answer === 'outdoor') score += region.scores.rural + region.scores.coastal;
            if (answer.answer === 'culture') score += region.scores.urban;
            if (answer.answer === 'peaceful') score += region.scores.rural;
            break;
        }
      });

      scores[region.id] = score;
    });

    return frenchRegions
      .map(region => ({ ...region, matchScore: scores[region.id] }))
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 3);
  };

  const topMatches = showResults ? calculateMatches() : [];
  const progress = ((currentQuestion + 1) / quizQuestions.length) * 100;

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setEmailSubmitted(true);
  };

  if (showResults) {
    if (!emailSubmitted) {
      return (
        <div className="max-w-xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card-elevated text-center"
          >
            <div className="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-5">
              <Mail className="w-8 h-8 text-accent-600" />
            </div>
            <h2 className="text-2xl font-semibold text-primary-800 mb-2">Your Results Are Ready</h2>
            <p className="text-primary-500 mb-6">
              Enter your email to see your personalised French region recommendations and receive our relocation guide.
            </p>
            <form onSubmit={handleEmailSubmit} className="max-w-sm mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="input-field mb-4"
              />
              <button type="submit" className="btn-accent w-full">
                See My Results <ArrowRight className="w-5 h-5" />
              </button>
            </form>
            <p className="text-xs text-primary-400 mt-4">
              We respect your privacy. Unsubscribe anytime.
            </p>
          </motion.div>
        </div>
      );
    }

    return (
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card-elevated"
        >
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-success-600" />
            </div>
            <h2 className="text-2xl font-semibold text-primary-800 mb-2">Your Perfect French Regions</h2>
            <p className="text-primary-500">Based on your preferences, here are your top matches</p>
          </div>

          <div className="space-y-5">
            {topMatches.map((region, index) => (
              <motion.div
                key={region.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.15 }}
                className={`rounded-lg overflow-hidden border-2 ${
                  index === 0 ? 'border-accent-400 bg-accent-50' : 'border-primary-100 bg-white'
                }`}
              >
                <div className="md:flex">
                  <div className="md:w-1/3 h-48 md:h-auto">
                    <img
                      src={region.image}
                      alt={region.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="p-5 md:w-2/3">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          {index === 0 && (
                            <span className="bg-accent-500 text-white text-xs px-2 py-0.5 rounded font-medium">
                              Best Match
                            </span>
                          )}
                          <span className="text-sm text-primary-400">#{index + 1}</span>
                        </div>
                        <h3 className="text-xl font-semibold text-primary-800">{region.name}</h3>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-primary-400 uppercase tracking-wide">Match</p>
                        <p className="text-2xl font-bold text-primary-700">{Math.round((region.matchScore / 50) * 100)}%</p>
                      </div>
                    </div>
                    <p className="text-primary-600 mb-4 text-sm">{region.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <div className="bg-white rounded p-2 border border-primary-100">
                        <p className="text-xs text-primary-400">Avg. Rent</p>
                        <p className="font-semibold text-primary-700 text-sm">€{region.avgRent}/mo</p>
                      </div>
                      <div className="bg-white rounded p-2 border border-primary-100">
                        <p className="text-xs text-primary-400">Climate</p>
                        <p className="font-semibold text-primary-700 text-sm">{region.climate}</p>
                      </div>
                      <div className="bg-white rounded p-2 border border-primary-100">
                        <p className="text-xs text-primary-400">Lifestyle</p>
                        <p className="font-semibold text-primary-700 text-sm">{region.lifestyle}</p>
                      </div>
                      <div className="bg-white rounded p-2 border border-primary-100">
                        <p className="text-xs text-primary-400">Expat Community</p>
                        <p className="font-semibold text-primary-700 text-sm">{region.expatCommunity}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-8 bg-primary-700 rounded-lg p-6 text-white">
            <p className="font-semibold text-lg mb-2">Found your ideal region?</p>
            <p className="text-primary-200 mb-4">
              Ibanista specialises in UK-to-France relocations. Let us help you make your dream move a reality.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="https://www.ibanista.com/contact"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-white text-primary-700 px-5 py-2.5 rounded font-medium hover:bg-primary-50 transition-colors"
              >
                Book Consultation <ExternalLink className="w-4 h-4" />
              </a>
              <button
                onClick={() => {
                  setAnswers([]);
                  setCurrentQuestion(0);
                  setShowResults(false);
                  setEmailSubmitted(false);
                }}
                className="inline-flex items-center gap-2 border-2 border-white/30 text-white px-5 py-2.5 rounded font-medium hover:bg-white/10 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Retake Quiz
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  const question = quizQuestions[currentQuestion];
  const QuestionIcon = question.icon;

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        key={currentQuestion}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        className="card-elevated"
      >
        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-primary-500 mb-2">
            <span>Question {currentQuestion + 1} of {quizQuestions.length}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
          <div className="h-1.5 bg-primary-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary-700"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <QuestionIcon className="w-6 h-6 text-primary-700" />
          </div>
          <h2 className="text-xl font-semibold text-primary-800">{question.question}</h2>
        </div>

        {/* Options */}
        <div className="grid gap-3">
          {question.options.map((option) => {
            const OptionIcon = option.icon;
            return (
              <motion.button
                key={option.value}
                onClick={() => handleAnswer(option.value)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-4 p-4 bg-primary-50 hover:bg-primary-100 border border-primary-100 hover:border-primary-300 rounded-lg transition-all text-left group"
              >
                <div className="w-10 h-10 bg-white group-hover:bg-primary-700 rounded-lg flex items-center justify-center transition-colors border border-primary-100 group-hover:border-primary-700">
                  <OptionIcon className="w-5 h-5 text-primary-600 group-hover:text-white transition-colors" />
                </div>
                <span className="font-medium text-primary-700 group-hover:text-primary-800 transition-colors flex-1">
                  {option.label}
                </span>
                <ChevronRight className="w-5 h-5 text-primary-300 group-hover:text-primary-500 transition-colors" />
              </motion.button>
            );
          })}
        </div>

        {currentQuestion > 0 && (
          <button
            onClick={() => {
              setCurrentQuestion(currentQuestion - 1);
              setAnswers(answers.slice(0, -1));
            }}
            className="mt-6 text-primary-500 hover:text-primary-700 font-medium flex items-center gap-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Previous question
          </button>
        )}
      </motion.div>
    </div>
  );
}

// Newsletter Section
function NewsletterSection() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-400 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-primary-400 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto px-4 relative z-10">
        <motion.div
          className="text-center"
          variants={fadeInUp}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-6">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Free Relocation Guides & Resources
          </h2>
          <p className="text-primary-200 text-lg mb-8 max-w-2xl mx-auto">
            Join 5,000+ expats getting weekly tips on moving to France, navigating bureaucracy,
            and building your new life abroad.
          </p>

          {!submitted ? (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                required
                className="flex-1 px-5 py-4 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-accent-400 focus:border-transparent"
              />
              <motion.button
                type="submit"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="btn-accent px-8 py-4 shadow-lg"
              >
                Subscribe <ArrowRight className="w-5 h-5" />
              </motion.button>
            </form>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white/10 backdrop-blur-sm rounded-lg p-6 max-w-md mx-auto"
            >
              <CheckCircle className="w-12 h-12 text-accent-400 mx-auto mb-4" />
              <p className="text-white font-semibold text-lg">Welcome aboard!</p>
              <p className="text-primary-200">Check your inbox for your first guide.</p>
            </motion.div>
          )}

          <p className="text-primary-300 text-sm mt-6">
            We respect your privacy. Unsubscribe anytime.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

// Main App
function App() {
  const [activeTab, setActiveTab] = useState<'calculator' | 'quiz'>('calculator');

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-primary-100">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="#" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-700 rounded flex items-center justify-center">
              <span className="text-white font-bold text-lg">i</span>
            </div>
            <div>
              <h1 className="font-semibold text-primary-800">Ibanista</h1>
              <p className="text-xs text-primary-400">UK to France Relocation</p>
            </div>
          </a>
          <div className="flex items-center gap-4">
            <a
              href="tel:+442033765117"
              className="hidden md:flex items-center gap-2 text-primary-600 hover:text-primary-800 text-sm font-medium"
            >
              <Phone className="w-4 h-4" />
              +44 203 376 5117
            </a>
            <a
              href="https://www.ibanista.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-800 font-medium flex items-center gap-1 text-sm"
            >
              Visit Ibanista.com <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Hero */}
      <HeroSection />

      {/* Trust Badges */}
      <TrustSection />

      {/* Services Preview */}
      <ServicesSection />

      {/* Tools Section */}
      <section id="tools" className="py-20 bg-gradient-to-b from-white to-primary-50">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div
            className="text-center mb-12"
            variants={fadeInUp}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-primary-800 mb-4">
              Interactive Planning Tools
            </h2>
            <p className="text-primary-600 text-lg max-w-2xl mx-auto">
              Use our free tools to estimate your budget and find your perfect French region.
            </p>
          </motion.div>

          {/* Tab Navigation */}
          <div className="max-w-2xl mx-auto mb-10">
            <div className="bg-white rounded-xl shadow-medium p-1.5 flex gap-1.5">
              <button
                onClick={() => setActiveTab('calculator')}
                className={`flex-1 py-3.5 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  activeTab === 'calculator'
                    ? 'bg-primary-700 text-white shadow-md'
                    : 'text-primary-600 hover:bg-primary-50'
                }`}
              >
                <Calculator className="w-5 h-5" />
                Budget Calculator
              </button>
              <button
                onClick={() => setActiveTab('quiz')}
                className={`flex-1 py-3.5 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                  activeTab === 'quiz'
                    ? 'bg-primary-700 text-white shadow-md'
                    : 'text-primary-600 hover:bg-primary-50'
                }`}
              >
                <MapPin className="w-5 h-5" />
                Region Finder
              </button>
            </div>
          </div>

          {/* Content */}
          <AnimatePresence mode="wait">
            {activeTab === 'calculator' ? (
              <motion.div
                key="calculator"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <RelocationCalculator />
              </motion.div>
            ) : (
              <motion.div
                key="quiz"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <RegionFinderQuiz />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* Newsletter Section */}
      <NewsletterSection />

      {/* Footer */}
      <footer className="bg-primary-900 text-primary-300 py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-10 mb-10">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-white rounded flex items-center justify-center">
                  <span className="text-primary-800 font-bold text-lg">i</span>
                </div>
                <span className="text-white font-semibold text-lg">Ibanista</span>
              </div>
              <p className="text-sm leading-relaxed mb-4">
                Real help from real people for your UK to France move.
              </p>
              <div className="flex items-center gap-1 mb-2">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-accent-400 text-accent-400" />
                ))}
              </div>
              <p className="text-xs">50+ five-star Trustpilot reviews</p>
            </div>

            {/* Services */}
            <div>
              <h4 className="text-white font-semibold mb-4">Services</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="https://www.ibanista.com/send-money-to-france/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Money Transfers</a></li>
                <li><a href="https://www.ibanista.com/find-long-term-rentals-in-france/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Long-Term Rentals</a></li>
                <li><a href="https://www.ibanista.com/moving-to-france-power-hour-11-strategy-session-with-ben-small/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Power Hour</a></li>
                <li><a href="https://www.ibanista.com/expat-care-package/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Expat Care Package</a></li>
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="text-white font-semibold mb-4">Free Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="https://www.ibanista.com/our-guides-and-e-books/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Guides & E-books</a></li>
                <li><a href="https://www.ibanista.com/blog/webinars/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Webinars</a></li>
                <li><a href="https://www.ibanista.com/blog/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Articles</a></li>
                <li><a href="https://www.ibanista.com/faqs-help-centre/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">FAQs</a></li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-3 text-sm">
                <li className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  <a href="tel:+442033765117" className="hover:text-white transition-colors">+44 203 376 5117</a>
                </li>
                <li className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  <a href="https://www.ibanista.com/contact/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Contact Form</a>
                </li>
                <li className="flex items-start gap-2">
                  <Building2 className="w-4 h-4 mt-0.5" />
                  <span>4th Floor Silverstream House<br />45 Fitzroy Street, London</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-primary-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs">
              <span>Ibanista Ltd (No. 14047903)</span>
              <a href="https://www.ibanista.com/security-regulation/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors flex items-center gap-1">
                <Shield className="w-3 h-3" /> FCA Regulated
              </a>
              <a href="https://www.ibanista.com/privacy-policy/" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Privacy Policy</a>
            </div>
            <div className="text-xs text-primary-400">
              Demo built by Matthew Scott | January 2026
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
