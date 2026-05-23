<template>
	<!-- 顶部标题区域 -->
	<div class="top-section">

		<h1 class="main-title">光影与故事的行旅</h1>
		<p class="intro-text">从节日里的万家灯火，到画卷中的一盏暖光，再到典故里的微弱烛焰，我们将三段叙事编织成一条光影长廊，邀请你沉浸式探索古灯文化。</p>
		
		<!-- 滚轮提示信息 -->
		<div v-if="showScrollTip" class="scroll-tip">
			请点击卡牌
		</div>
		
		<!-- 主要导航按钮 -->
		<div class="main-nav">
			<div v-for="(item, index) in navigationItems" :key="index" class="nav-card"
				:class="{ 'clicked': activeCardIndex >= 0 }"
				@click="onNavClick(item.id, index)">
				<div class="nav-card-inner" :class="{ 'flipped': activeCardIndex === index }">
					<div class="nav-card-front">
						<div class="nav-card-content">
							<div class="nav-card-icon">
								<img :src="item.iconPath" :alt="item.name" @error="handleImageError($event)">
							</div>
							<div class="nav-card-title">{{ item.name }}</div>
						</div>
					</div>
					<div class="nav-card-back">
						<div class="nav-card-back-content">
							<div class="nav-card-description">{{ item.description }}</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- 节日内容统一容器 -->
	<div v-if="activeCardIndex === 0" ref="festivalRef" id="festival" class="section-content">
		<video 
			:src="video1" 
			controls 
			preload="metadata" 
			poster=""
			@load="handleVideoLoad"
			class="fullscreen-video"
		></video>
	</div>

	<div v-if="activeCardIndex === 1" ref="paintingsRef" id="paintings" class="section-content">
		<!-- 画作展示区域 -->
		<div class="paintings-section">

			<!-- 封面元素 -->
			<div v-if="!showPaintings" class="paintings-cover" @click="togglePaintings">
				<!-- 漂浮光点 -->
				<div class="floating-light"></div>
				<div class="floating-light"></div>
				<div class="floating-light"></div>
				<div class="floating-light"></div>
				<div class="floating-light"></div>
				<div class="floating-light"></div>
				
				<div class="cover-content">
					<h3>探索画中灯</h3>
					<p class="cover-description">点击查看古代画作中的灯具艺术</p>
					<div class="lantern-decoration">
						<div class="lantern-top"></div>
						<div class="lantern-bottom"></div>
						<div class="lantern-tassel"></div>
					</div>
				</div>
			</div>

			<!-- 画作画廊 -->
			<div v-if="showPaintings" class="paintings-gallery">
				<div v-for="(relic, index) in allPaintings" :key="index" class="painting-item"
					:class="getPaintingClass(index)" @mouseenter="hoveredRelic = relic"
					@mouseleave="hoveredRelic = null">
					<div class="painting-container">
						<img :src="relic.imageUrl" :alt="relic.name" class="painting-image" @error="handleImageError($event)">
						<div v-if="hoveredRelic === relic" class="painting-tooltip">
							<h5>{{ relic.name }}</h5>
							<p>{{ relic.description }}</p>
							<p class="painting-period">时期：{{ relic.period }}</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<div v-if="activeCardIndex === 2" ref="storiesRef" id="stories" class="section-content">
		<!-- 故事展示区域 - 小册子效果 -->
		
			<div class="booklet-container">
				<!-- 小册子主体 -->
				<div class="booklet" :class="{ flipped: isFlipped }">
					<!-- 封面 -->
					<div class="booklet-cover" @click="toggleBooklet">
						<div class="cover-content">
							<h3>灯事会</h3>
							<p class="cover-subtitle">点击翻阅历史典故</p>
							<div class="lantern-decoration"></div>
						</div>
					</div>

					<!-- 内页内容 -->
					<div class="booklet-inner">
						<!-- 左侧页面 -->
						<div class="page left-page" :class="{ active: currentPageIndex === 0 }">
							<div class="page-content">
								<h5 class="page-title">{{ currentStory.title }}</h5>
								<p class="page-intro">{{ currentStory.introduction }}</p>
								<button class="details-button" @click="showDetails = true">
									查看详细内容
								</button>
							</div>
						</div>

						<!-- 右侧页面 -->
						<div class="page right-page" :class="{ active: currentPageIndex > 0 }">
							<div class="page-content">
								<h5 class="page-number">典故 {{ currentPageIndex + 1 }}/{{ totalStories }}</h5>
								<div class="navigation-controls">
									<button class="nav-button prev" @click="goToPreviousPage"
										:disabled="currentPageIndex === 0">
										上一页
									</button>
									<button class="nav-button next" @click="goToNextPage"
										:disabled="currentPageIndex === totalStories - 1">
										下一页
									</button>
								</div>
							</div>
						</div>
					</div>
				

				<!-- 详细内容弹窗 -->
				<div v-if="showDetails" class="details-modal" @click="showDetails = false">
					<div class="modal-content" @click.stop>
						<button class="close-button" @click="showDetails = false">×</button>
						<h4 class="modal-title">{{ currentStory.title }}</h4>
						<div class="modal-details">
							<p>{{ currentStory.details }}</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
	/**
	 * 文化页面组件 - 展示传统文化内容，包括节日、古灯画作和历史故事
	 * 功能特点：
	 * - 全屏视频展示节日内容
	 * - 响应式设计，适配各种设备
	 * - 优化的性能和交互体验
	 */
	import {
		ref,
		computed,
		onMounted,
		onUnmounted
	} from 'vue';
	import axios from 'axios';


	// 导入视频文件
	import video1 from '../../video/video1.mp4';

	const storyData = [{
			id: 1,
			title: '《艺文类聚》引《尚书大传》卷五载',
			introduction: `晋平公问师旷曰："吾年七十，欲学，恐已暮。"
师旷曰："臣闻老而学者，如执烛之明。执烛之明，孰与昧行？"公曰："善。"`,
			details: '这段"师旷论学"的记载同时也出现在西汉刘向的《说苑》中。师旷本是盲乐师，面对晋平公暮年求学时的担忧，他巧妙回应道，老年求学如手持灯烛前行，灯烛之明虽然不及日光，但总要强过蒙昧夜行。生而有涯，但学无止境，古人将灯烛比作求学悟道过程中的指引，它们既是智慧本身，也是人们追求智慧过程中需要具备的志向与恒心。'
		},
		{
			id: 2,
			title: '《韩非子·外储说左上》',
			introduction: '郢人有遗燕相国书者，夜书，火不明，因谓持烛者曰"举烛"而误书"举烛"。举烛，非书意也。燕相国受书而说之，曰："举烛者，尚明也；尚明也者，举贤而任之。"燕相白王，王大说，国以治。',
			details: '故事中，一个楚国人晚上要写信给燕国的宰相，因为照明的火炬不够亮，于是他让侍从将火炬举高点，一边说一边误在信上写下"举烛"两字。燕国的宰相曲解其意，借以向燕王阐释任贤之道，于时燕国大治。对此，韩非子指出"治则治矣，非书意也"，并以此讽刺了当时学人在治学过程中的穿凿附会与断章取义。\n  \n尽管燕相的说辞是一种误读，但他将举烛与选贤关联起来，则赋予了灯烛新的意涵，后世的咏烛诗中也常可见燕相举烛任贤的典故。'
		},
		{
			id: 3,
			title: '《梁书·陆云公传》',
			introduction: '云公善弈棋，尝夜侍御坐，武冠触烛火，高祖笑谓曰："烛烧卿貂。"高祖将用云公为侍中，故以此言戏之也。',
			details: '梁代的陆云公擅长下棋，常在夜间陪梁武帝侍坐。有一次在下棋时，他的武冠碰到了烛火。这本是颇为尴尬之事，恰好梁武帝想要提拔陆云公，便顺势将此事视为升迁的吉兆。这个故事虽然简短，却反映了古人对灯烛的特殊情感和文化内涵。'
		},
		{
			id: 4,
			title: '《旧唐书·刘沔传》',
			introduction: '初，沔为忠武小校，从李光颜讨淮西，为捉生将。前后遇贼血战，锋刃所伤，几死者数四。尝伤重卧草中，月黑不知归路，昏然而睡，梦人授之双烛，曰：“子方大贵，此行无患，可持此而还。”既行，炯然有双光在前。自后破虏危难，每行常有此光。及罢镇后，双光息。',
			details: '《旧唐书·刘沔传》中记载了一个颇为离奇的事件：刘沔以前在追随李光颜征讨淮西时，为了生擒敌将，前后血战，负伤数次。有一回，他伤重卧于草中，因月黑而不知归路。睡梦中有人授以双烛，并告知他此行无患，可持灯而还。醒来以后，他眼前两束烛光炯然。从此以后，每回出行都会有这两束光出现在眼前。此事究竟是真是假难以详察，但至少可以说明，灯烛当时是照亮人命运前路的一种意象。'
		}
	];

	export default {
		name: 'CulturePage',
		setup() {
			// ========== 导航相关 ==========
			/**
			 * 导航菜单项目
			 * 对应页面的三个主要区域：节日、画中灯、灯事会
			 */
			const navigationItems = ref([{
		name: '节日',
		id: 'festival',
		iconPath: '/icons/icon(5).png',
		description: '探索传统节日中的灯火文化，感受万家灯火的温暖与喜庆。'
	},
	{
		name: '画中灯',
		id: 'paintings',
		iconPath: '/icons/icon(10).png',
		description: '欣赏古代画作中的灯具艺术，了解不同时期的灯具有特色。'
	},
	{
		name: '灯事会',
		id: 'stories',
		iconPath: '/icons/icon(6).png',
		description: '翻阅历史典故中的灯事传说，感受灯文化的深厚底蕴。'
	}
]);
const currentPage = ref(0); // 0: 节日, 1: 画中灯, 2: 灯事会
const activeCardIndex = ref(-1); // 当前激活的卡片索引，-1表示无激活卡片
const showScrollTip = ref(false); // 滚轮提示信息显示状态

// 页面分区引用
const festivalRef = ref(null);
const paintingsRef = ref(null);
const storiesRef = ref(null);

// 平滑滚动到页面分区
const scrollToSection = (id) => {
	const map = {
		festival: festivalRef,
		paintings: paintingsRef,
		stories: storiesRef
	};
	const target = map[id]?.value;
	if (target && typeof target.scrollIntoView === 'function') {
		target.scrollIntoView({
			behavior: 'smooth',
			block: 'start'
		});
	}
};

const handleImageError = (e) => {
	e.target.src = 'http://localhost:5000/static/images/logo.jpg';
	console.warn('图片加载失败，已使用默认图片替代');
};

// 滚轮事件处理
const handleWheel = (event) => {
	// 显示提示信息
	showScrollTip.value = true;
	// 3秒后隐藏提示信息
	setTimeout(() => {
		showScrollTip.value = false;
	}, 3000);
};

const onNavClick = (id, index) => {
		// 设置当前激活的卡片索引
		activeCardIndex.value = index;
		// 更新当前页面
		currentPage.value = index;
		// 重置画中灯的显示状态，确保切换到其他卡牌时恢复封面
		showPaintings.value = false;
		// 重置灯事会的显示状态，确保切换到其他卡牌时恢复封面
		isFlipped.value = false;
		showDetails.value = false;
		// 滚动到对应区域
		setTimeout(() => {
			scrollToSection(id);
		}, 100);
	};

	// 生命周期钩子
	onMounted(() => {
		// 添加滚轮事件监听
		window.addEventListener('wheel', handleWheel, { passive: false });
	});

	onUnmounted(() => {
		// 移除滚轮事件监听
		window.removeEventListener('wheel', handleWheel);
	});

			// ========== 视频相关 ==========
			/**
			 * 当前悬停的文物对象
			 * 用于显示画作的详情提示框
			 */
			const hoveredRelic = ref(null);

			/**
			 * 控制是否显示画作
			 * 初始为false，点击封面后变为true
			 */
			const showPaintings = ref(false);

			/**
			 * 点击封面显示画作
			 */
			const togglePaintings = () => {
				showPaintings.value = true;
			};

			/**
			 * 视频相关
			 * 现在使用上下排布的固定布局，不再需要轮播功能
			 */

			/**
			 * 视频资源路径
			 * 用于展示节日相关视频内容
			 */
			// 视频路径已通过import导入，无需重复定义

			// 新增：independentPaintingsData数组
			const allPaintings = ref([]);

			// 从后端获取画中灯数据
			const fetchPaintings = async () => {
				try {
					const res = await axios.get('http://localhost:5000/api/paintings');
					allPaintings.value = res.data;
				} catch (error) {
					console.warn('Failed to fetch paintings:', error);
				}
			};

			// ========== 小册子翻页相关 ==========
			/**
			 * 小册子是否翻转到内页
			 * @type {boolean}
			 */
			const isFlipped = ref(false);

			/**
			 * 当前页面索引
			 * @type {number}
			 */
			const currentPageIndex = ref(0);

			/**
			 * 是否显示详情弹窗
			 * @type {boolean}
			 */
			const showDetails = ref(false);

			/**
			 * 总故事数量
			 * @type {number}
			 */
			const totalStories = storyData.length;

			/**
			 * 当前显示的故事
			 * @type {Object}
			 */
			const currentStory = computed(() => {
				return storyData[currentPageIndex.value] || storyData[0];
			});

			/**
			 * 翻转小册子
			 * @returns {void}
			 */
			const toggleBooklet = () => {
				console.log('Toggle booklet clicked, current isFlipped:', isFlipped.value);
				isFlipped.value = !isFlipped.value;
				console.log('After toggle, isFlipped:', isFlipped.value);
			};

			/**
			 * 翻到下一页
			 * @returns {void}
			 */
			const goToNextPage = () => {
				if (currentPageIndex.value < totalStories - 1) {
					// 添加翻页动画效果
					const rightPage = document.querySelector('.right-page');
					if (rightPage) {
						rightPage.style.animation = 'pageFlip 0.6s ease';
						setTimeout(() => {
							rightPage.style.animation = '';
						}, 600);
					}

					currentPageIndex.value++;
				}
			};

			/**
			 * 翻到上一页
			 * @returns {void}
			 */
			const goToPreviousPage = () => {
				if (currentPageIndex.value > 0) {
					// 添加翻页动画效果
					const rightPage = document.querySelector('.right-page');
					if (rightPage) {
						rightPage.style.animation = 'pageFlip 0.6s ease';
						setTimeout(() => {
							rightPage.style.animation = '';
						}, 600);
					}

					currentPageIndex.value--;
				}
			};

			// ========== 布局相关 ==========
			/**
			 * 根据索引获取画作的布局类名
			 * 确保画廊布局多样化，提高视觉吸引力
			 * @param {number} index - 画作的索引
			 * @returns {string} 对应的CSS类名
			 */
			const getPaintingClass = (index) => {
				if (index === 0) return 'large-portrait';
				if (index === 1) return 'medium-portrait';
				if (index === 2) return 'small-landscape';
				if (index === 3) return 'medium-landscape';
				// 对于后续画作，循环使用布局
				const mod = index % 4;
				if (mod === 0) return 'medium-portrait';
				if (mod === 1) return 'small-landscape';
				if (mod === 2) return 'medium-landscape';
				if (mod === 3) return 'large-portrait';
				return '';
			};

			// ========== 视频优化 ==========
			/**
			 * 视频加载完成处理函数
			 * 优化视频加载体验，移除加载动画
			 * @param {Event} event - 视频加载事件对象
			 * @returns {void}
			 */
			const handleVideoLoad = (event) => {
				const video = event.target;
				// 视频加载完成后移除加载动画
				const videoContainer = video.closest('.tab-v');
				if (videoContainer) {
					videoContainer.classList.add('video-loaded');
				}
				// 视频加载完成后设置为暂停状态，等待用户交互再播放
				if (video.preload === 'metadata') {
					video.pause();
				}
			};

			/**
			 * 设置视频播放策略
			 * 实现延迟加载和按需播放，提高页面性能
			 * @returns {void}
			 */
			const setupVideos = () => {
				// 获取所有视频元素
				const videos = document.querySelectorAll('video');

				// 为每个视频添加事件监听，确保用户交互后才播放
				videos.forEach((video, index) => {
					// 第一个视频只预加载元数据
					if (index === 0) {
						video.preload = 'metadata';
					}
					// 其他视频完全按需加载
					else {
						video.preload = 'none';
					}

					// 初始状态都暂停
					video.pause();
					video.currentTime = 0;

					// 添加延迟加载逻辑
					if (index > 0) {
						// 当视频进入视口时才加载
						const observer = new IntersectionObserver(
							(entries) => {
								entries.forEach(entry => {
									if (entry.isIntersecting) {
										// 视频进入视口，开始加载
										video.load();
										observer.disconnect(); // 加载后停止观察
									}
								});
							}, {
								threshold: 0.5
							}
						);
						observer.observe(video);
					}
				});
			};

			// 创建防抖函数
			const debounce = (func, wait) => {
				let timeout;
				return function executedFunction(...args) {
					const later = () => {
						clearTimeout(timeout);
						func(...args);
					};
					clearTimeout(timeout);
					timeout = setTimeout(later, wait);
				};
			};

			// 优化的滚动处理逻辑
			const lastScrollTop = ref(0); // 移到函数外部，避免每次调用都重新创建

			const handleScroll = debounce(() => {
				const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
				const navBar = document.querySelector('.navigation-bar');

				// 使用requestAnimationFrame优化UI更新
				requestAnimationFrame(() => {
					if (navBar) {
						// 优化滚动时导航栏效果
						const isScrollingDown = scrollTop > lastScrollTop.value;
						const hasScrolledPastThreshold = scrollTop > 100;

						if (isScrollingDown && hasScrolledPastThreshold) {
							// 向下滚动 - 平滑隐藏导航栏
							navBar.style.transition = 'top 0.3s ease, opacity 0.3s ease';
							navBar.style.top = '-120px';
							navBar.style.opacity = '0.8';
						} else {
							// 向上滚动或回到顶部 - 平滑显示导航栏
							navBar.style.transition =
								'top 0.3s ease, opacity 0.3s ease, box-shadow 0.3s ease';
							navBar.style.top = '0';
							navBar.style.opacity = '1';

							// 滚动时导航栏阴影增强 - 基于滚动位置
							if (scrollTop > 50) {
								navBar.style.boxShadow =
									'0 10px 30px rgba(160, 82, 45, 0.25), ' +
									'0 0 40px rgba(218, 165, 32, 0.15), ' +
									'inset 0 1px 0 rgba(255, 255, 255, 0.8)';
							} else {
								navBar.style.boxShadow = '';
							}
						}
					}
				});

				// 检测当前可见区域，更新当前页面 - 只在滚动足够距离时更新
				if (Math.abs(scrollTop - lastScrollTop.value) > 30) {
					const sections = [{
							id: 'festival',
							element: festivalRef.value
						},
						{
							id: 'paintings',
							element: paintingsRef.value
						},
						{
							id: 'stories',
							element: storiesRef.value
						}
					].filter(item => item.element);

					// 使用IntersectionObserver的逻辑，但通过滚动事件实现
					for (const section of sections) {
						const rect = section.element.getBoundingClientRect();
						const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
						// 当元素占据视口的30%以上时认为可见
						const isElementVisible = rect.top < viewportHeight * 0.7 && rect.bottom > viewportHeight *
							0.3;

						if (isElementVisible) {
							const index = navigationItems.value.findIndex(item => item.id === section.id);
							if (index !== -1 && currentPage.value !== index) {
								// 平滑更新当前页面状态
								requestAnimationFrame(() => {
									currentPage.value = index;
								});
							}
							break;
						}
					}
				}

				// 更新最后的滚动位置
				lastScrollTop.value = scrollTop <= 0 ? 0 : scrollTop;
			}, 50); // 50ms防抖，平衡响应速度和性能

			// ========== 生命周期 ==========
			/**
			 * 组件挂载后执行
			 * 设置视频和添加滚动事件监听
			 */
			onMounted(() => {
				// 初始化视频播放策略
				setupVideos();
				// 添加滚动事件监听
				window.addEventListener('scroll', handleScroll);
				// 从后端获取画中灯数据
				fetchPaintings();
			});

			// 在组件卸载时统一清理滚动事件监听
			onUnmounted(() => {
				window.removeEventListener('scroll', handleScroll);
			});

			/**
			 * 返回组件暴露的属性和方法
			 * 供模板中使用的数据和函数
			 */
			return {
				navigationItems,
				currentPage,
				activeCardIndex,
				showScrollTip,
				onNavClick,
				allPaintings,
				hoveredRelic,
				showPaintings,
				togglePaintings,
				video1,
				festivalRef,
				paintingsRef,
				storiesRef,
				getPaintingClass,
				handleVideoLoad,
				// 小册子翻页相关
				isFlipped,
				toggleBooklet,
				currentPageIndex,
				totalStories,
				currentStory,
				showDetails,
				goToNextPage,
				goToPreviousPage
			};
		}
}
</script>

<style scoped>
	/**
	 * 组件样式定义
	 * 包括布局、主题风格和响应式设计
	 * 采用古灯主题风格，温暖典雅
	 */
	/* 基础样式重置 */
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
		font-family: "宋体";
		
	}

	body {
		background-color: #fff9e6;
		/* 优化背景图案，添加灯笼和光晕元素 */

		color: #8b5a2b;
		line-height: 1.6;
		/* 添加平滑滚动 */
		scroll-behavior: smooth;
	}

	/* 全局容器样式 */
	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 0 20px;
	}

	/* 全局标题样式 */
	h1,
	h2,
	h3,
	h4,
	h5,
	h6 {
		font-family: "Ma Shan Zheng";
		color: #a0522d;
		font-weight: 400;
	}

	/* 全局段落样式 */
	p {
		font-family: "宋体";
		color: #8b5a2b;
		line-height: 1.8;
	}

	/* 全局按钮样式 */
	button {
		font-family: "宋体";
		cursor: pointer;
		transition: all 0.3s ease;
	}

	/* 顶部区域样式 */
	.top-section {
		text-align: center;
		padding: 35px 20px 10px;
		max-width: 1200px;
		margin: 0 auto;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}

	.subtitle {
		font-size: 24px;
		color: #a0522d;
		margin-bottom: 20px;
		font-weight: normal;
		letter-spacing: 2px;
	}

	.main-title {
		font-size: 48px;
		color: #5d4037;
		margin-bottom: 30px;
		font-weight: normal;
		letter-spacing: 3px;
		text-shadow: 2px 2px 4px rgba(139, 69, 19, 0.2);
	}

	.intro-text {
		font-size: 18px;
		color: #8b5a2b;
		max-width: 900px;
		margin: 0 auto 40px;
		line-height: 1.8;
		text-align: center;
		padding: 0 20px;
	}

	/* 滚轮提示信息 */
	.scroll-tip {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background-color: white;
		color: black;
		padding: 10px 20px;
		border-radius: 8px;
		font-size: 12px;
		z-index: 1000;
		animation: fadeInOut 3s ease-in-out;
	}

	@keyframes fadeInOut {
		0% { opacity: 0; }
		10% { opacity: 1; }
		90% { opacity: 1; }
		100% { opacity: 0; }
	}

	/* 主要导航按钮 */
	.main-nav {
		display: flex;
		justify-content: center;
		gap: 30px;
		margin-bottom: 20px;
		flex-wrap: wrap;
	}

	.nav-card {
		width: 200px;
		height: 280px;
		cursor: pointer;
		perspective: 1000px;
	}

	.nav-card-inner {
		position: relative;
		width: 100%;
		height: 100%;
		text-align: center;
		transition: transform 0.8s ease;
		transform-style: preserve-3d;
	}

	.nav-card:not(.clicked):hover .nav-card-inner {
		transform: rotateY(180deg);
	}

	.nav-card-inner.flipped {
		transform: rotateY(180deg);
	}

	.nav-card-front, .nav-card-back {
		position: absolute;
		width: 100%;
		height: 100%;
		backface-visibility: hidden;
		border-radius: 12px;
		border: 2px solid #d4a76a;
		padding: 20px;
		box-shadow: 0 4px 16px rgba(139, 69, 19, 0.1);
	}

	.nav-card-front {
		background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 245, 230, 0.85) 100%);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.nav-card-back {
		background: linear-gradient(135deg, rgba(218, 165, 32, 0.9) 0%, rgba(184, 134, 11, 0.9) 100%);
		transform: rotateY(180deg);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.nav-card-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 15px;
		height: 100%;
		justify-content: center;
	}

	.nav-card-icon {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 2px 8px rgba(139, 69, 19, 0.15);
	}

	.nav-card-icon img {
		width: 60px;
		height: 60px;
		object-fit: contain;
	}

	.nav-card-title {
		font-size: 20px;
		font-weight: 600;
		color: #8b4513;
		text-align: center;
	}

	.nav-card-back-content {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
	}

	.nav-card-description {
		font-size: 16px;
		color: #fff;
		text-align: center;
		line-height: 1.5;
	}

	.nav-card:hover {
		transform: translateY(-4px);
	}

	.nav-card:hover .nav-card-front {
		box-shadow: 0 8px 24px rgba(139, 69, 19, 0.2), 0 0 24px rgba(218, 165, 32, 0.15);
	}

	.nav-card:hover .nav-card-back {
		box-shadow: 0 8px 24px rgba(139, 69, 19, 0.25), 0 0 30px rgba(218, 165, 32, 0.2);
	}

	/* 全屏视频样式 */
	.fullscreen-video {
		width: 100vw;
		height: 100vh;
		object-fit: cover;
		position: relative;
		z-index: 1;
		background-color: #000;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.fullscreen-video {
			width: 100vw;
			height: 100vh;
			object-fit: cover;
		}
	}

	/* 页面布局调整 */
	.top-section {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 60px 20px;
	}

	.section-content {
		margin-top: 0;
		padding: 0;
		max-width: 100%;
		margin-left: 0;
		margin-right: 0;
		display: flex;
		flex-direction: column;
		align-items: stretch;
		justify-content: flex-start;
		min-height: 100vh;
		width: 100vw;
		overflow: visible;
		position: relative;
		z-index: 2;
	}

	

	/* 响应式设计 */
	@media (max-width: 768px) {
		.top-section {
			min-height: auto;
			padding: 40px 20px;
		}

		.section-content {
			margin-top: 30px;
			padding: 20px;
		}
	}

	/* 导航栏样式 - 隐藏原来的导航栏 */
	.navigation-bar {
		display: none;
	}

	.navigation-bar button {
		padding: 15px 28px;
		border: 1px solid #e0e0e0;
		border-radius: 10px;
		font-size: 18px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		background-color: #ffffff;
		min-width: 160px;
	}

	/* 节日按钮样式 */
	.navigation-bar button:nth-child(1) {
		background-color: #ffffff;
		color: #333333;
	}

	/* 画中灯按钮样式 */
	.navigation-bar button:nth-child(2) {
		background-color: #d4b483;
		color: #ffffff;
		border: 1px solid #c0a063;
	}

	/* 灯事会按钮样式 */
	.navigation-bar button:nth-child(3) {
		background-color: #f0e6d2;
		color: #333333;
		border: 1px solid #e0d6c2;
	}

	/* 激活状态 */
	.navigation-bar button.active {
		transform: scale(1.03);
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
	}

	/* 图标样式 */
	.nav-icon {
		width: 24px;
		height: 24px;
		object-fit: contain;
		vertical-align: middle;
	}

	/* 按钮悬停效果 */
	.navigation-bar button:hover {
		transform: translateY(-1px);
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		
	}

	/* ========== 小册子翻页效果样式 ========== */
	.booklet-container {
		width: 100%;
		max-width: 800px;
		margin: 0 auto;
		padding: 40px 0 80px;
		perspective: 1200px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	/* 小册子主体 */
	.booklet {
		width: 100%;
		height: 500px;
		position: relative;
		transform-style: preserve-3d;
		transition: transform 0.6s ease;
		cursor: pointer;
	}

	/* 封面样式 */
	.booklet-cover {
		position: absolute;
		width: 100%;
		height: 100%;
		backface-visibility: hidden;
		background: linear-gradient(135deg, #c18b5d 0%, #a87c4a 100%);
		border-radius: 5px;
		box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
		border: 3px solid #d2b48c;
		display: flex;
		align-items: center;
		justify-content: center;
		transform: rotateY(0deg);
		transition: all 0.5s ease;
	}

	.booklet-cover:hover {
		transform: scale(1.02) rotateY(0deg);
		box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 215, 0, 0.2);
	}

	.cover-content {
			text-align: center;
			color: #fff9e6;
			padding: 40px;
			background-size: cover;
			background-position: center;
			background-repeat: no-repeat;
		}

	.cover-content h3 {
		font-size: 42px;
		margin-bottom: 20px;
		text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
		letter-spacing: 2px;
	}

	.cover-subtitle {
		font-size: 18px;
		opacity: 0.9;
		margin-bottom: 40px;
		font-style: italic;
	}

	/* 灯笼装饰 - 使用图标 */
	.lantern-decoration {
		width: 80px;
		height: 80px;
		background-image: url('/icons/icon (2).png');
		background-size: contain;
		background-repeat: no-repeat;
		background-position: center;
		margin: 0 auto;
		position: relative;
		animation: lantern-swing 4s ease-in-out infinite;
	}

	@keyframes lantern-swing {

		0%,
		100% {
			transform: rotate(-3deg) scale(1);
		}

		50% {
			transform: rotate(3deg) scale(1.05);
		}
	}

	/* 内页容器 */
	.booklet-inner {
		position: absolute;
		width: 100%;
		height: 100%;
		backface-visibility: hidden;
		transform: rotateY(180deg);
		transition: all 0.5s ease;
		display: flex;
		perspective: 800px;
	}

	/* 页面翻转状态 */
	.booklet.flipped .booklet-cover {
		transform: rotateY(-180deg);
	}

	.booklet.flipped .booklet-inner {
		transform: rotateY(0deg);
	}

	/* 页面通用样式 */
	.page {
		width: 50%;
		height: 100%;
		background: #fff9e6;
		display: flex;
		flex-direction: column;
		padding: 40px 30px;
		position: relative;
		backface-visibility: hidden;
		transition: all 0.4s ease;
	}

	.left-page {
		border-right: 2px solid #d2b48c;
		box-shadow: inset -5px 0 15px rgba(139, 69, 19, 0.1);
		transform-origin: left center;
	}

	.right-page {
		border-left: 2px solid #d2b48c;
		box-shadow: inset 5px 0 15px rgba(139, 69, 19, 0.1);
		transform-origin: right center;
	}

	.page-content {
		height: 100%;
		width: 100%;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		position: relative;
		color: #8b4513;
	}

	/* 页面标题和内容 */
	.page-title {
		font-size: 24px;
		color: #8b4513;
		margin-bottom: 25px;
		padding-bottom: 15px;
		border-bottom: 2px solid #d2b48c;
		text-align: center;
		font-weight: bold;
	}

	.page-intro {
		font-size: 16px;
		line-height: 1.8;
		color: #654321;
		margin-bottom: 30px;
		flex: 1;
		text-align: justify;
		text-indent: 2em;
	}

	.page-number {
		font-size: 16px;
		color: #8b4513;
		text-align: center;
		margin-bottom: 40px;
		opacity: 0.8;
		font-style: italic;
	}

	/* 详细内容按钮 */
	.details-button {
		background: linear-gradient(135deg, #8b4513 0%, #6b340f 100%);
		color: #fff9e6;
		border: none;
		padding: 12px 24px;
		font-size: 16px;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.3s ease;
		margin-top: auto;
		align-self: center;
		text-transform: uppercase;
		letter-spacing: 1px;
		font-weight: 600;
		box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
	}

	.details-button:hover {
		background: linear-gradient(135deg, #6b340f 0%, #8b4513 100%);
		transform: translateY(-2px);
		box-shadow: 0 6px 16px rgba(139, 69, 19, 0.4);
	}

	/* 导航按钮 */
	.navigation-controls {
		display: flex;
		justify-content: space-between;
		margin-top: auto;
	}

	.nav-button {
		background: linear-gradient(135deg, #d2b48c 0%, #b8a078 100%);
		color: #8b4513;
		border: none;
		padding: 12px 24px;
		font-size: 16px;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.3s ease;
		font-weight: 600;
		box-shadow: 0 4px 10px rgba(139, 69, 19, 0.2);
	}

	.nav-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #b8a078 0%, #d2b48c 100%);
		transform: translateY(-2px);
		box-shadow: 0 6px 14px rgba(139, 69, 19, 0.3);
	}

	.nav-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	/* 详细内容弹窗 */
	.details-modal {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.3s ease;
	}

	.modal-content {
		background: #fff9e6;
		border-radius: 10px;
		width: 90%;
		max-width: 800px;
		max-height: 80vh;
		padding: 40px;
		position: relative;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
		animation: slideIn 0.3s ease;
		overflow-y: auto;
		border: 3px solid #d2b48c;
	}

	.close-button {
		position: absolute;
		top: 20px;
		right: 20px;
		background: none;
		border: none;
		font-size: 32px;
		color: #8b4513;
		cursor: pointer;
		transition: all 0.3s ease;
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
	}

	.close-button:hover {
		background: #d2b48c;
		color: #fff9e6;
		transform: scale(1.1);
	}

	.modal-title {
		font-size: 28px;
		color: #8b4513;
		margin-bottom: 25px;
		text-align: center;
		padding-bottom: 15px;
		border-bottom: 2px solid #d2b48c;
	}

	.modal-details p {
		font-size: 18px;
		line-height: 1.8;
		color: #654321;
		text-align: justify;
		text-indent: 2em;
	}

	/* 动画效果 */
	@keyframes fadeIn {
		from {
			opacity: 0;
		}

		to {
			opacity: 1;
		}
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-50px) scale(0.9);
		}

		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	/* 翻页动画效果 */
	@keyframes pageFlip {
		0% {
			transform: rotateY(0deg);
		}

		50% {
			transform: rotateY(90deg);
		}

		100% {
			transform: rotateY(0deg);
		}
	}

	/* 页面加载动画 */
	@keyframes pageLoad {
		from {
			opacity: 0;
			transform: translateY(20px);
		}

		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.page.active {
		animation: pageLoad 0.5s ease forwards;
	}

	/* 标签栏 - 古灯主题 */
	.tab-bar {
		display: flex;
		justify-content: center;
		margin: 30px auto;
		gap: 15px;
		flex-wrap: wrap;
		position: relative;
		padding: 15px;
		max-width: 600px;
		background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
		border-radius: 8px 8px 0 0;
		border-bottom: 2px solid #ffd79a;
		box-shadow: 0 2px 6px rgba(139, 69, 19, 0.1);
	}

	.tab-bar::before {
		content: '';
		position: absolute;
		top: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 90%;
		height: 2px;
		background: linear-gradient(to right, transparent, #d4a76a, transparent);
		box-shadow: 0 0 10px rgba(218, 165, 32, 0.1);
	}

	.tab-bar button {
		padding: 10px 20px;
		border: none;
		background: linear-gradient(to bottom, #fff3d6, #ffe8c1);
		color: #8b5a2b;
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.3s ease;
		position: relative;
		overflow: hidden;
		font-size: 16px;
		font-weight: 500;
		text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.7);
		/* border-bottom: 2px solid transparent; */
		box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
	}

	.tab-bar button:hover {
		background: linear-gradient(to bottom, #ffe8c1, #fff3d6);
		color: #a0522d;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(184, 134, 11, 0.3);
		border-color: #b8860b;
		border-bottom-color: #ffd79a;
	}

	.tab-bar button.active {
		background: linear-gradient(to bottom, #fff3d6, #ffd79a);
		color: #8b4513;
		font-weight: 600;
		border-color: #b8860b;
		/* border-bottom: 2px solid #ffd79a; */
		box-shadow: 0 2px 4px rgba(139, 69, 19, 0.1);
	}

	.tab-bar button:focus-visible {
		box-shadow: 0 0 0 3px rgba(218, 165, 32, 0.4);
	}

	@media (prefers-reduced-motion: reduce) {

		.tab-bar button,
		.tab-bar button.active {
			transition: none;
		}
	}

	/* 内容区域 - 古灯主题 */
	.tab-content {
		width: 95%;
		height: auto;
		min-height: 500px;
		display: flex;
		flex-wrap: wrap;
		padding: 25px;
		position: relative;
		background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
		border: 1px solid #ffd79a;
		border-radius: 0 0 8px 8px;
		box-shadow: 0 3px 10px rgba(139, 69, 19, 0.1);
		margin: 0 auto 40px auto;
		max-width: 1200px;
		backdrop-filter: blur(8px);
	}

	

	.tab-content::before {
		content: '';
		position: absolute;
		inset: 0;
		background:
			url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="%23f0e6d8" stroke-width="0.5" opacity="0.3"/></svg>'),
			radial-gradient(circle at top, rgba(255, 215, 0, 0.1) 0%, transparent 30%);
		pointer-events: none;
	}

	/* 视频容器 - 优化版古灯主题 */
	/* 视频容器 - 优化版古灯主题 */
	

	.tab-v:hover video {
		transform: scale(1.005);
		filter: brightness(1.05);
	}

	.tab-v:hover {
		transform: translateY(-5px);
		box-shadow:
			0 20px 40px rgba(0, 0, 0, 0.15),
			0 0 30px rgba(218, 165, 32, 0.15),
			0 1px 0 rgba(255, 255, 255, 0.2) inset;
		border-color: rgba(218, 165, 32, 0.4);
	}

	/* 视频加载动画 */
	.tab-v:not(.video-loaded)::before {
		content: '';
		position: absolute;
		inset: 0;
		background-image: linear-gradient(45deg, rgba(218, 165, 32, 0.3) 0%, transparent 50%, rgba(218, 165, 32, 0.3) 100%);
		background-size: 200% 200%;
		animation: borderGlow 2s ease infinite;
		border-radius: 14px;
		z-index: 2;
	}

	/* 视频加载完成后的状态 */
	.tab-v.video-loaded::before {
		content: '';
		position: absolute;
		inset: 0;
		opacity: 1;
		background: linear-gradient(135deg, rgba(218, 165, 32, 0.1) 0%, transparent 50%, rgba(218, 165, 32, 0.1) 100%);
		animation: borderGlow 6s ease infinite;
		border-radius: 14px;
		z-index: 2;
	}

	/* ========== 响应式设计支持 ========== */

	/* 平板设备 (768px - 1024px) */
	@media (max-width: 1024px) {

		/* 调整视频容器 */
		.tab-v {
			max-width: 90%;
			aspect-ratio: 16/6;
			width: 100%;
			margin: 0 auto;
			border-radius: 14px;
			box-shadow:
				0 12px 30px rgba(0, 0, 0, 0.1),
				0 0 20px rgba(218, 165, 32, 0.08);
			border: 2px solid rgba(218, 165, 32, 0.2);
		}

		/* 调整视频容器布局 */
		.video-carousel {
			max-width: 95%;
			padding: 20px;
			gap: 30px;
			margin: 35px auto 50px;
		}

		/* 调整导航栏 */
		.navigation-bar {
			padding: 10px 5px;
		}

		.navigation-bar button {
			padding: 8px 15px;
			font-size: 14px;
		}

		.nav-icon {
			width: 24px;
			height: 24px;
		}

		/* 调整画作布局 */
		/* 封面样式 */
		.paintings-cover {
			width: 100%;
			height: 100vh;
			min-height: 100px;
			background: linear-gradient(135deg, #f7e9cd 0%, #f3d8a7 100%);
			border-radius: 0;
			position: relative;
			display: flex;
			align-items: center;
			justify-content: center;
			cursor: pointer;
			transition: all 0.3s ease;
			box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
			overflow: hidden;
		}

		/* 四角中国结装饰 */
		.paintings-cover::after {
			content: '';
			position: absolute;
			inset: 20px;
			border: 2px solid rgba(160, 82, 45, 0.1);
			border-radius: 10px;
			pointer-events: none;
		}

		/* 漂浮光点效果 */
		.paintings-cover .floating-light {
			position: absolute;
			border-radius: 50%;
			background: radial-gradient(circle, rgba(212, 167, 106, 0.6) 0%, transparent 70%);
			animation: float 6s ease-in-out infinite;
			pointer-events: none;
		}

		.paintings-cover .floating-light:nth-child(1) {
			width: 60px;
			height: 60px;
			top: 20%;
			left: 15%;
			animation-delay: 0s;
		}

		.paintings-cover .floating-light:nth-child(2) {
			width: 40px;
			height: 40px;
			top: 60%;
			right: 10%;
			animation-delay: 2s;
		}

		.paintings-cover .floating-light:nth-child(3) {
			width: 50px;
			height: 50px;
			top: 80%;
			left: 25%;
			animation-delay: 4s;
		}

		@keyframes float {
			0%, 100% {
				transform: translateY(0px) scale(1);
				opacity: 0.5;
			}
			50% {
				transform: translateY(-20px) scale(1.1);
				opacity: 0.8;
			}
		}

		.paintings-cover:hover {
			transform: translateY(-5px);
			box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15), 0 0 40px rgba(212, 167, 106, 0.3);
		}

		/* 增强标题视觉效果 */
		.cover-content h3 {
			font-size: 42px;
			margin-bottom: 15px;
			font-family: 'SimSun', 'STSong', serif;
			font-weight: bold;
			letter-spacing: 3px;
			text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
			background: linear-gradient(135deg, #a0522d 0%, #d2691e 100%);
			-webkit-background-clip: text;
			-webkit-text-fill-color: transparent;
			background-clip: text;
			transition: all 0.3s ease;
		}

		.cover-content h3:hover {
			transform: scale(1.05);
			text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.15);
		}

		.paintings-cover::before {
			content: '';
			position: absolute;
			inset: 0;
			
			pointer-events: none;
		}

		.cover-content {
			text-align: center;
			color: #8b5a2b;
			z-index: 1;
			padding: 40px;
		}

		.cover-content h3 {
			font-size: 42px;
			margin-bottom: 15px;
			font-family: 'SimSun', 'STSong', serif;
			font-weight: bold;
			letter-spacing: 3px;
			text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
		}

		.cover-description {
			font-size: 18px;
			margin-bottom: 30px;
			line-height: 1.6;
			color: #a06d40;
			max-width: 600px;
			margin-left: auto;
			margin-right: auto;
		}

		/* 装饰性灯笼 */
		.lantern-decoration {
			position: relative;
			width: 100px;
			height: 150px;
			margin: 20px auto 0;
			transform-origin: top center;
			animation: lanternSway 4s ease-in-out infinite;
		}

		.lantern-decoration::before {
			content: '';
			position: absolute;
			width: 100px;
			height: 150px;
			background: linear-gradient(135deg, #e84118 0%, #c23616 100%);
			border-radius: 50px / 20px;
			opacity: 0.9;
			box-shadow: 0 0 20px rgba(230, 126, 34, 0.6);
			animation: lanternGlow 3s ease-in-out infinite alternate;
		}

		.lantern-decoration::after {
			content: '';
			position: absolute;
			width: 80px;
			height: 130px;
			background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
			border-radius: 40px / 15px;
			left: 10px;
			top: 10px;
			opacity: 0.8;
		}

		/* 灯笼顶部装饰 */
		.lantern-decoration .lantern-top {
			position: absolute;
			top: -15px;
			left: 50%;
			transform: translateX(-50%);
			width: 30px;
			height: 30px;
			background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
			clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
			z-index: 1;
		}

		/* 灯笼底部装饰 */
		.lantern-decoration .lantern-bottom {
			position: absolute;
			bottom: -10px;
			left: 50%;
			transform: translateX(-50%);
			width: 40px;
			height: 20px;
			background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
			border-radius: 0 0 20px 20px;
			z-index: 1;
		}

		/* 灯笼流苏 */
		.lantern-decoration .lantern-tassel {
			position: absolute;
			bottom: -30px;
			left: 50%;
			transform: translateX(-50%);
			width: 4px;
			height: 30px;
			background: #f1c40f;
			border-radius: 2px;
			z-index: 1;
		}

		@keyframes lanternGlow {
			0% {
				box-shadow: 0 0 10px rgba(230, 126, 34, 0.6);
			}

			100% {
				box-shadow: 0 0 30px rgba(230, 126, 34, 0.9);
			}
		}

		@keyframes lanternSway {
			0%, 100% {
				transform: rotate(-2deg);
			}
			50% {
				transform: rotate(2deg);
			}
		}

		/* 点击提示动画 */
		.paintings-cover:hover .cover-content h3 {
			transform: scale(1.05);
			transition: transform 0.3s ease;
		}

		/* 响应式设计 */
		@media (max-width: 768px) {
			.paintings-cover {
				height: 300px;
				padding: 20px;
			}

			.cover-content h3 {
				font-size: 32px;
				letter-spacing: 2px;
			}

			.cover-description {
				font-size: 16px;
				padding: 0 10px;
			}

			.lantern-decoration {
				width: 80px;
				height: 120px;
			}

			.lantern-decoration::before {
				width: 80px;
				height: 120px;
			}

			.lantern-decoration::after {
				width: 64px;
				height: 104px;
				left: 8px;
				top: 8px;
			}
		}

		@media (max-width: 480px) {
			.paintings-cover {
				height: 250px;
			}

			.cover-content {
				padding: 20px;
			}

			.cover-content h3 {
				font-size: 24px;
				margin-bottom: 10px;
			}

			.cover-description {
				font-size: 14px;
				margin-bottom: 20px;
			}

			.lantern-decoration {
				width: 60px;
				height: 90px;
			}

			.lantern-decoration::before {
				width: 60px;
				height: 90px;
			}

			.lantern-decoration::after {
				width: 48px;
				height: 78px;
				left: 6px;
				top: 6px;
			}
		}

		/* 不规则画廊布局 - 古灯主题优化版 */
		.paintings-gallery {
			grid-template-columns: repeat(2, 1fr);
			gap: 20px;
		}

		/* 调整文字大小 */
		.video-description p {
			font-size: 15px;
			line-height: 1.8;
		}

		.video-section h3 {
			font-size: 28px;
			margin-bottom: 25px;
		}
	}

	/* 移动设备 (小于768px) */
	@media (max-width: 768px) {

		/* 视频容器适应移动设备 */
		.tab-v {
			max-width: 95%;
			aspect-ratio: 16/9;
			width: 100%;
			margin: 0 auto;
			border-radius: 12px;
			box-shadow:
				0 10px 25px rgba(0, 0, 0, 0.08),
				0 0 15px rgba(218, 165, 32, 0.06);
			border: 1px solid rgba(218, 165, 32, 0.15);
		}

		/* 移动设备下无视频描述 */

		/* 调整视频元素 */
		.tab-v video,
		.tab-v>video {
			border-radius: 10px;
		}

		/* 调整视频加载动画 */
		.tab-v:not(.video-loaded)::before,
		.tab-v.video-loaded::before {
			border-radius: 10px;
		}

		/* 调整视频容器布局 */
		.video-carousel {
			max-width: 100%;
			padding: 15px 10px;
			gap: 20px;
			margin: 20px auto 30px;
			border-radius: 12px;
		}

		/* 调整视频板块标题 */
		.video-section h3 {
			font-size: 24px;
			margin-bottom: 20px;
			padding-bottom: 15px;
		}

		/* 垂直排列导航栏 */
		.navigation-bar {
			flex-direction: column;
			gap: 8px;
			padding: 15px 10px;
		}

		.navigation-bar button {
			padding: 10px 20px;
			font-size: 16px;
			width: 100%;
		}

		.nav-icon {
			width: 28px;
			height: 28px;
		}

		/* 单列布局画作 */
		.paintings-gallery {
			grid-template-columns: 1fr;
			gap: 25px;
		}

		/* 调整容器边距 */
		.container {
			padding: 0 15px;
		}

		.video-carousel {
			padding: 15px;
			margin-bottom: 30px;
			gap: 20px;
		}

		/* 优化文字阅读体验 */
		.video-description p {
			font-size: 14px;
			line-height: 1.8;
			text-indent: 1.5em;
		}

		.video-section h3 {
			font-size: 24px;
			margin-bottom: 20px;
			padding-bottom: 15px;
		}

		/* 调整故事区域 */
		.story-container {
			padding: 0 5px;
		}

		.story-item {
			margin-bottom: 25px;
		}

		.story-header {
			padding: 15px;
		}

		.story-details {
			padding: 15px;
		}
	}

	/* 小屏幕移动设备 (小于480px) */
	@media (max-width: 480px) {
		.tab-v {
			height: 40vh;
		}

		.navigation-bar button {
			padding: 8px 15px;
			font-size: 14px;
		}

		.nav-icon {
			width: 24px;
			height: 24px;
		}

		.video-description {
			padding: 20px 15px;
		}

		.video-section h3 {
			font-size: 20px;
		}
	}


	.tab-icontent h3 {
		color: #a0522d;
		margin-bottom: 20px;
		font-size: 26px;
		text-align: center;
		text-shadow: 1px 1px 2px rgba(160, 82, 45, 0.2);
		position: relative;
		padding-bottom: 15px;
		font-weight: bold;
	}

	.tab-icontent h3::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 70%;
		height: 2px;
		background: linear-gradient(to right, transparent, #d4a76a, transparent);
		box-shadow: 0 0 10px rgba(218, 165, 32, 0.2);
	}

	.tab-icontent p {
		color: #8b5a2b;
		line-height: 1.8;
		margin-bottom: 18px;
		font-size: 15px;
	}

	.content-details {
		margin-top: 25px;
		padding-top: 20px;
		border-top: 1px solid rgba(218, 165, 32, 0.3);
	}

	.content-details p {
		margin-bottom: 15px;
		font-size: 15px;
		color: #8b5a2b;
		text-indent: 2em;
		line-height: 1.8;
	}

	/* 自定义滚动条 - 古灯主题 */
	.tab-icontent::-webkit-scrollbar {
		width: 8px;
	}

	.tab-icontent::-webkit-scrollbar-thumb {
		background: #b8860b;
		border-radius: 4px;
		border: 2px solid #e8ded0;
	}

	.tab-icontent::-webkit-scrollbar-track {
		background: #e8ded0;
		border-radius: 4px;
	}

	/* 画作展示区域样式 - 让封面 / 画廊铺满整个区域 */
	.paintings-section {
		margin: 0;
		padding: 0;
		position: relative;
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: stretch;
		justify-content: flex-start;
	}

	/* 确保封面占满整个区域 */
	.paintings-cover {
		width: 100%;
		height: 100vh;
		min-height: 500px;
		background: linear-gradient(135deg, #f7e9cd 0%, #f3d8a7 100%);
		border-radius: 0;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: none;
		overflow: hidden;
		z-index: 1;
	}

	/* 确保画廊能正常显示 */
	.paintings-gallery {
		display: grid;
		grid-template-columns: repeat(12, 1fr);
		grid-auto-rows: minmax(240px, auto);
		gap: 30px;
		max-width: 1300px;
		margin: 0 auto;
		padding: 35px;
		position: relative;
	}

	

	.paintings-section h4 {
		color: #8b5a2b;
		font-size: 36px;
		margin-bottom: 40px;
		text-align: center;
		text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
		position: relative;
		padding-bottom: 25px;
		font-family: 'SimSun', 'STSong', serif;
		font-weight: bold;
		letter-spacing: 2px;
	}

	.paintings-section h4::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 50%;
		height: 4px;
		background: linear-gradient(to right, transparent, #d4a76a, transparent);
		box-shadow: 0 0 20px rgba(218, 165, 32, 0.4);
		border-radius: 2px;
	}

	/* 画廊封面 - 牌匾式卷轴效果（全局适用） */
	.paintings-cover {
		width: 100%;
		height: 100vh;
		background: linear-gradient(135deg, #f7e9cd 0%, #f3d8a7 100%);
		border-radius: 0;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow:
			0 8px 25px rgba(0, 0, 0, 0.12),
			inset 0 0 0 1px rgba(255, 255, 255, 0.6);
		overflow: hidden;
	}



	/* 漂浮光点效果 */
	.paintings-cover .floating-light {
		position: absolute;
		border-radius: 50%;
		background: radial-gradient(circle, rgba(212, 167, 106, 0.6) 0%, transparent 70%);
		animation: float 6s ease-in-out infinite;
		pointer-events: none;
	}

	.paintings-cover .floating-light:nth-child(1) {
		width: 60px;
		height: 60px;
		top: 20%;
		left: 15%;
		animation-delay: 0s;
	}

	.paintings-cover .floating-light:nth-child(2) {
		width: 40px;
		height: 40px;
		top: 60%;
		right: 10%;
		animation-delay: 2s;
	}

	.paintings-cover .floating-light:nth-child(3) {
		width: 50px;
		height: 50px;
		top: 78%;
		left: 25%;
		animation-delay: 4s;
	}

	.paintings-cover .floating-light:nth-child(4) {
		width: 30px;
		height: 30px;
		top: 35%;
		right: 20%;
		animation-delay: 1s;
	}

	.paintings-cover .floating-light:nth-child(5) {
		width: 45px;
		height: 45px;
		top: 15%;
		right: 30%;
		animation-delay: 3s;
	}

	.paintings-cover .floating-light:nth-child(6) {
		width: 35px;
		height: 35px;
		top: 50%;
		left: 8%;
		animation-delay: 5s;
	}

	@keyframes float {
		0%,
		100% {
			transform: translateY(0px) scale(1);
			opacity: 0.5;
		}

		50% {
			transform: translateY(-20px) scale(1.1);
			opacity: 0.8;
		}
	}

	/* 封面文字区域，保持与整页风格一致 */
	.paintings-cover .cover-content {
		text-align: center;
		color: #8b5a2b;
		z-index: 1;
		padding: 40px 60px;
		max-width: 620px;
		margin: 0 auto;
	}

	.paintings-cover .cover-content h3 {
		font-size: 42px;
		margin-bottom: 15px;
		font-family: 'Ma Shan Zheng';
		font-weight: bold;
		letter-spacing: 3px;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
		background: linear-gradient(135deg, #a0522d 0%, #d2691e 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		transition: all 0.3s ease;
	}

	.paintings-cover .cover-content h3:hover {
		transform: scale(1.05);
		text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.15);
	}

	.paintings-cover .cover-description {
		font-size: 18px;
		margin-bottom: 30px;
		line-height: 1.7;
		color: #7a4a24;
	}

	/* 封面专用灯笼，避免影响其他位置的 .lantern-decoration */
	.paintings-cover .lantern-decoration {
		position: relative;
		width: 100px;
		height: 150px;
		margin: 20px auto 0;
		transform-origin: top center;
		animation: lanternSway 4s ease-in-out infinite;
	}

	.paintings-cover .lantern-top {
		position: absolute;
		top: -15px;
		left: 50%;
		transform: translateX(-50%);
		width: 30px;
		height: 30px;
		background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
		clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
		z-index: 1;
	}

	.paintings-cover .lantern-bottom {
		position: absolute;
		bottom: -10px;
		left: 50%;
		transform: translateX(-50%);
		width: 40px;
		height: 20px;
		background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
		border-radius: 0 0 20px 20px;
		z-index: 1;
	}

	.paintings-cover .lantern-tassel {
		position: absolute;
		bottom: -30px;
		left: 50%;
		transform: translateX(-50%);
		width: 4px;
		height: 30px;
		background: #f1c40f;
		border-radius: 2px;
		z-index: 1;
	}

	@keyframes lanternSway {
		0%,
		100% {
			transform: rotate(-2deg);
		}

		50% {
			transform: rotate(2deg);
		}
	}

	.paintings-cover:hover {
		transform: translateY(-5px);
		box-shadow:
			0 15px 30px rgba(0, 0, 0, 0.15),
			0 0 40px rgba(212, 167, 106, 0.3);
	}

	/* 不规则画廊布局 - 古灯主题优化版 */
	.paintings-gallery {
		display: grid;
		grid-template-columns: repeat(12, 1fr);
		grid-auto-rows: minmax(240px, auto);
		gap: 30px;
		max-width: 1300px;
		margin: 0 auto;
		padding: 35px;
		position: relative;
		width: 100%;
		min-height: 100vh;
	}

	.painting-item {
		cursor: pointer;
		transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
		border-radius: 16px;
		border: 3px solid #d4a76a;
		background: linear-gradient(135deg, #fff9e6 0%, #fff3d6 100%);
		box-shadow:
			0 5px 20px rgba(139, 69, 19, 0.1),
			0 0 0 1px rgba(255, 255, 255, 0.8);
		position: relative;
		overflow: hidden;
		transform-origin: center;
	}

	.painting-item::before {
		content: '';
		position: absolute;
		inset: 0;
		background:
			radial-gradient(circle at top left, rgba(218, 165, 32, 0.2) 0%, transparent 50%),
			radial-gradient(circle at bottom right, rgba(255, 215, 0, 0.15) 0%, transparent 60%);
		pointer-events: none;
	}

	.painting-item:hover {
		transform: translateY(-8px) scale(1.02);
		box-shadow:
			0 15px 35px rgba(160, 82, 45, 0.25),
			0 0 25px rgba(255, 215, 0, 0.3),
			inset 0 0 20px rgba(255, 255, 255, 0.8);
		border-color: #ffd79a;
		animation: lantern-glow 2s ease infinite;
	}

	.painting-item:hover::after {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		border: 3px solid #ffd79a;
		border-radius: 16px;
		box-shadow:
			0 0 30px rgba(255, 215, 0, 0.4),
			0 0 50px rgba(255, 215, 0, 0.2);
		pointer-events: none;
		opacity: 0.8;
		animation: borderGlow 3s ease infinite;
	}

	@keyframes lantern-glow {

		0%,
		100% {
			box-shadow: 0 0 15px rgba(218, 165, 32, 0.5);
		}

		50% {
			box-shadow: 0 0 25px rgba(218, 165, 32, 0.8);
		}
	}

	/* 不同大小的画作布局 */
	.painting-item.large-portrait {
		grid-column: span 4;
		grid-row: span 2;
	}

	.painting-item.medium-portrait {
		grid-column: span 3;
		grid-row: span 2;
	}

	.painting-item.medium-landscape {
		grid-column: span 5;
		grid-row: span 1;
	}

	.painting-item.small-landscape {
		grid-column: span 4;
		grid-row: span 1;
	}

	.painting-container {
		position: relative;
		width: 100%;
		height: 100%;
		overflow: hidden;
		border-radius: 12px;
		padding: 16px;
		background: linear-gradient(135deg, #ffffff 0%, #fff9e6 100%);
		box-shadow:
			inset 0 3px 15px rgba(0, 0, 0, 0.08),
			inset 0 0 0 1px rgba(255, 255, 255, 0.9);
		transition: all 0.3s ease;
	}

	.painting-image {
		width: 100%;
		height: 100%;
		object-fit: contain;
		background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
		transition: transform 0.4s ease, filter 0.4s ease;
		border-radius: 8px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
	}

	.painting-item:hover .painting-image {
		transform: scale(1.05);
		filter: brightness(1.2) contrast(1.1);
	}

	.painting-tooltip {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		padding: 25px;
		background: linear-gradient(135deg, rgba(255, 249, 230, 0.98) 0%, rgba(255, 235, 205, 0.98) 100%);
		color: #8b5a2b;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		text-align: center;
		opacity: 1;
		animation: fadeIn 0.4s ease;
		border: 2px solid rgba(218, 165, 32, 0.6);
		border-radius: 12px;
		box-sizing: border-box;
		text-shadow: none;
		box-shadow:
			0 8px 30px rgba(139, 69, 19, 0.15),
			inset 0 2px 10px rgba(255, 255, 255, 0.9);
	}

	.painting-tooltip h5 {
		font-size: 19px;
		margin-bottom: 12px;
		color: #a0522d;
		font-weight: bold;
		text-shadow: 1px 1px 2px rgba(160, 82, 45, 0.2);
		font-family: 'SimSun', 'STSong', serif;
	}

	.painting-tooltip p {
		font-size: 15px;
		color: #8b5a2b;
		margin-bottom: 10px;
		max-height: 30vh;
		overflow-y: auto;
		padding-right: 10px;
		line-height: 1.7;
		text-align: left;
		text-indent: 2em;
	}

	.painting-period {
		font-size: 13px;
		color: #b8860b;
		font-style: italic;
		margin-top: 12px;
		border-top: 1px dotted rgba(218, 165, 32, 0.3);
		padding-top: 10px;
	}

	/* 自定义滚动条 - 画作提示框 */
	.painting-tooltip p::-webkit-scrollbar {
		width: 6px;
	}

	.painting-tooltip p::-webkit-scrollbar-thumb {
		background: #d4a76a;
		border-radius: 3px;
		border: 1px solid #fff3d6;
	}

	.painting-tooltip p::-webkit-scrollbar-track {
		background: #fff3d6;
		border-radius: 3px;
	}

	/* 故事展示区域样式 - 古灯主题优化版 */
	.story {
		margin:  auto;
		padding: 45px 35px;
		background-color: #e8ded0;
		border-radius: 20px;
		position: relative;
	
		margin-bottom: 80px;
		max-width: 1400px;
		width: 95%;
		backdrop-filter: blur(10px);
	}

	.story::before {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	/* 装饰性边框角 */
	.story::after {
		content: '';
		position: absolute;
		inset: -8px;
		background-size: 300% 300%;
		pointer-events: none;
		opacity: 0.5;
		border-radius: 24px;
		z-index: -1;
		animation: borderGlow 8s ease infinite;
	}

	.story h4 {
		color: #a0522d;
		font-size: 36px;
		margin-bottom: 40px;
		text-align: center;
		text-shadow: 3px 3px 5px rgba(160, 82, 45, 0.25);
		position: relative;
		padding-bottom: 25px;
		font-family: 'SimSun', 'STSong', serif;
		font-weight: bold;
		letter-spacing: 2px;
	}

	.story h4::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 50%;
		height: 4px;
		background: linear-gradient(to right, transparent, #d4a76a, transparent);
		box-shadow: 0 0 20px rgba(218, 165, 32, 0.4);
		border-radius: 2px;
	}

	.story-container {
		display: flex;
		flex-direction: column;
		gap: 40px;
		padding: 35px;
		position: relative;
	}

	.story-item {
		background: linear-gradient(135deg, #fff9e6 0%, #fff3d6 100%);
		border-radius: 18px;
		border: 3px solid #d4a76a;
		box-shadow:
			0 8px 25px rgba(0, 0, 0, 0.15),
			0 0 30px rgba(218, 165, 32, 0.15),
			inset 0 1px 0 rgba(255, 255, 255, 0.9);
		padding: 40px;
		transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
		position: relative;
		overflow: hidden;
		transform-origin: center;
	}

	.story-item::before {
		content: '';
		position: absolute;
		inset: 0;
		background:
			radial-gradient(circle at top right, rgba(218, 165, 32, 0.2) 0%, transparent 50%),
			radial-gradient(circle at bottom left, rgba(255, 215, 0, 0.15) 0%, transparent 60%);
		pointer-events: none;
	}

	.story-item:hover {
		box-shadow:
			0 15px 40px rgba(160, 82, 45, 0.25),
			0 0 45px rgba(255, 215, 0, 0.3),
			inset 0 0 20px rgba(255, 255, 255, 0.8);
		transform: translateY(-8px) scale(1.01);
		border-color: #ffd79a;
		animation: lantern-glow 2s ease infinite;
	}

	.story-item:hover::after {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		border: 3px solid #ffd79a;
		border-radius: 18px;
		box-shadow:
			0 0 30px rgba(255, 215, 0, 0.4),
			0 0 50px rgba(255, 215, 0, 0.2);
		pointer-events: none;
		opacity: 0.8;
		animation: borderGlow 3s ease infinite;
	}

	.story-header h5 {
		color: #a0522d;
		font-size: 24px;
		font-weight: bold;
		margin-bottom: 25px;
		border-left: 4px solid #b8860b;
		padding-left: 22px;
		text-shadow: 2px 2px 4px rgba(160, 82, 45, 0.25);
		font-family: 'SimSun', 'STSong', serif;
		letter-spacing: 1px;
	}

	.story-intro {
		color: #8b5a2b;
		padding: 25px;
		line-height: 1.9;
		margin-bottom: 25px;
		font-size: 16px;
		background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 250, 240, 0.8) 100%);
		border-radius: 12px;
		border-left: 3px solid #b8860b;
		text-indent: 2em;
		text-shadow: none;
		box-shadow:
			inset 0 2px 10px rgba(0, 0, 0, 0.08),
			0 1px 3px rgba(255, 255, 255, 0.9);
		transition: all 0.3s ease;
	}

	.story-button {
		background: linear-gradient(135deg, rgba(255, 240, 215, 0.95) 0%, rgba(255, 230, 180, 0.95) 100%);
		color: #8b4513;
		border: 2px solid #ffd79a;
		padding: 14px 32px;
		border-radius: 12px;
		cursor: pointer;
		font-size: 16px;
		font-weight: 600;
		transition: all 0.4s ease;
		outline: none;
		position: relative;
		overflow: hidden;
		text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.7);
		box-shadow:
			0 4px 12px rgba(139, 69, 19, 0.15),
			0 0 0 1px rgba(255, 255, 255, 0.8);
		backdrop-filter: blur(10px);
		z-index: 1;
	}

	.story-button::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
		transition: all 0.6s ease;
		z-index: -1;
	}

	.story-button:hover {
		background: linear-gradient(135deg, rgba(255, 230, 180, 0.95) 0%, rgba(255, 210, 150, 0.95) 100%);
		box-shadow:
			0 6px 20px rgba(139, 69, 19, 0.2),
			0 0 15px rgba(255, 215, 0, 0.3);
		transform: translateY(-3px) scale(1.05);
		border-color: #ffd79a;
		color: #654321;
		z-index: 10;
	}

	.story-button:hover::before {
		left: 100%;
	}

	.story-button.active {
		background: linear-gradient(to bottom, #ffd700, #f0c14b);
		box-shadow:
			0 0 25px rgba(218, 165, 32, 0.5),
			inset 0 1px 0 rgba(255, 255, 255, 0.5),
			0 0 40px rgba(255, 215, 0, 0.3);
		border-color: #b8860b;
		color: #8b4513;
		transform: scale(1.05);
		z-index: 10;
	}

	.story-details {
		margin-top: 30px;
		padding: 30px;
		border-top: 2px dashed rgba(218, 165, 32, 0.4);
		animation: fadeIn 0.5s ease-in-out;
		background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 245, 230, 0.95) 100%);
		border-radius: 15px;
		position: relative;
		box-shadow:
			0 6px 15px rgba(139, 69, 19, 0.12),
			inset 0 1px 3px rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(5px);
	}

	.story-details::before {
		content: '✦';
		color: #b8860b;
		position: absolute;
		top: -12px;
		left: 30px;
		background: #fff3d6;
		padding: 0 12px;
		font-size: 16px;
		border-radius: 50%;
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 2px 8px rgba(184, 134, 11, 0.3);
		border: 1px solid rgba(255, 215, 0, 0.5);
	}

	.story-details p {
		color: #8b5a2b;
		line-height: 2.0;
		white-space: pre-wrap;
		font-size: 16px;
		text-indent: 2em;
		text-shadow: none;
		transition: all 0.3s ease;
	}

	.story-item:hover .story-details p {
		color: #654321;
		letter-spacing: 0.5px;
	}

	/* 节日容器样式 */
	.festival-container {
		background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
		border: 1px solid #ffd79a;
		border-radius: 8px;
		margin: 20px auto;
		max-width: 1200px;
		width: 95%;
		box-shadow: 0 3px 10px rgba(139, 69, 19, 0.1);
		overflow: hidden;
		backdrop-filter: blur(8px);
	}

	/* 响应式调整 - 古灯主题 */
	@media (max-width: 1024px) {
		.festival-container {
			background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
			border: 1px solid #ffd79a;
			border-radius: 8px;
			box-shadow: 0 3px 8px rgba(139, 69, 19, 0.1);
		}

		.navigation-bar {
			padding: 15px 20px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border-bottom: 2px solid #ffd79a;
			border-radius: 8px;
			backdrop-filter: blur(8px);
		}

		.navigation-bar button {
			padding: 8px 16px;
			font-size: 14px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border: 1px solid #ffd79a;
			color: #8b4513;
			font-weight: 500;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.1);
			backdrop-filter: blur(8px);
		}

		.navigation-bar button:hover {
			background: linear-gradient(135deg, rgba(255, 230, 180, 0.9) 0%, rgba(255, 210, 150, 0.9) 100%);
			border-color: #ffd79a;
			color: #654321;
			box-shadow: 0 3px 10px rgba(139, 69, 19, 0.12), 0 0 8px rgba(255, 215, 0, 0.15);
		}

		.tab-bar {
			margin: 20px;
			gap: 10px;
			flex-direction: column;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border-bottom: 2px solid #ffd79a;
			border-radius: 8px;
			backdrop-filter: blur(8px);
		}

		.tab-bar button {
			padding: 12px 20px;
			border-radius: 8px;
			text-align: center;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border: 1px solid #ffd79a;
			color: #8b4513;
			font-weight: 500;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.1);
		}

		.tab-bar button.active {
			background: linear-gradient(135deg, rgba(255, 230, 180, 0.9) 0%, rgba(255, 210, 150, 0.9) 100%);
			border-color: #ffd79a;
			color: #654321;
			box-shadow: 0 3px 10px rgba(139, 69, 19, 0.12);
		}

		.tab-content {
			margin: 20px;
			padding: 25px;
			background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
			border: 1px solid #ffd79a;
			border-radius: 8px;
			backdrop-filter: blur(8px);
			box-shadow: 0 3px 10px rgba(139, 69, 19, 0.1);
		}

		.tab-v {
			max-height: 300px;
			border: 2px solid #ffd79a;
			border-radius: 8px;
		}

		.tab-icontent {
			padding: 20px;
			background-color: #ffffff;
			color: #8b5a2b;
			border-radius: 8px;
		}

		.paintings-section,
		.story {
			margin: 30px auto;
			padding: 30px 20px;
			max-width: 900px;
			width: 95%;
			background-color: #e8ded0;
			border: 2px solid #ffd79a;
			border-radius: 12px;
		}

		.paintings-gallery {
			grid-template-columns: repeat(8, 1fr);
			gap: 20px;
			padding: 15px;
		}

		.painting-item.large-portrait {
			grid-column: span 4;
			grid-row: span 2;
			border: 2px solid #ffd79a;
		}

		.painting-item.medium-portrait {
			grid-column: span 4;
			grid-row: span 2;
			border: 2px solid #ffd79a;
		}

		.painting-item.medium-landscape {
			grid-column: span 5;
			border: 2px solid #ffd79a;
		}

		.painting-item.small-landscape {
			grid-column: span 3;
			border: 2px solid #ffd79a;
		}

		.painting-item:hover {
			box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15), 0 0 35px rgba(218, 165, 32, 0.2);
		}

		.paintings-section h4,
		.story h4 {
			font-size: 26px;
			color: #a0522d;
			background-color: #e8ded0;
		}

		.story-container {
			padding: 15px;
			gap: 20px;
		}

		.story-item {
			padding: 20px;
			border: 2px solid #ffd79a;
			background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 50%, #fff3d6 100%);
		}

		.story-header h5 {
			font-size: 17px;
			color: #a0522d;
		}

		.story-intro {
			font-size: 14px;
			color: #8b5a2b;
		}

		.story-button {
			background: linear-gradient(to bottom, #fff3d6, #ffe8c1);
			border: 2px solid #ffd79a;
			color: #8b5a2b;
		}

		.story-details p {
			font-size: 14px;
			color: #8b5a2b;
		}
	}

	@media (max-width: 768px) {
		.festival-container {
			background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
			border: 1px solid #ffd79a;
			border-radius: 8px;
			box-shadow: 0 3px 6px rgba(139, 69, 19, 0.08);
			margin: 15px auto;
		}

		.navigation-bar {
			flex-direction: column;
			gap: 10px;
			padding: 10px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border-radius: 8px;
			backdrop-filter: blur(8px);
		}

		.navigation-bar button {
			padding: 10px 20px;
			font-size: 16px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border: 1px solid #ffd79a;
			color: #8b4513;
			font-weight: 500;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.1);
			backdrop-filter: blur(8px);
		}

		.tab-bar {
			margin: 0 10px;
			gap: 8px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border-radius: 8px;
			backdrop-filter: blur(8px);
		}

		.tab-bar button {
			padding: 10px 16px;
			font-size: 14px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border: 1px solid #ffd79a;
			color: #8b4513;
			font-weight: 500;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.1);
		}

		.tab-content {
			margin: 20px 10px;
			padding: 15px;
			background: linear-gradient(135deg, #fff3d6 0%, #ffe8c1 100%);
			border: 1px solid #ffd79a;
			border-radius: 8px;
			backdrop-filter: blur(8px);
			box-shadow: 0 3px 8px rgba(139, 69, 19, 0.1);
		}

		.tab-v {
			border: 2px solid #d4a76a;
		}

		.tab-icontent {
			font-size: 14px;
			color: #8b5a2b;
			background-color: #ffffff;
		}

		.paintings-section,
		.story {
			margin: 20px auto;
			padding: 20px 15px;
			max-width: 500px;
			width: 95%;
			background-color: #e8ded0;
			border: 1px solid #ffd79a;
			border-radius: 8px;
			box-shadow: 0 3px 8px rgba(139, 69, 19, 0.1);
			backdrop-filter: blur(8px);
		}

		.paintings-section h4,
		.story h4 {
			font-size: 18px;
			margin-bottom: 20px;
			color: #a0522d;
		}

		.paintings-gallery {
			grid-template-columns: repeat(6, 1fr);
			grid-template-rows: auto;
			gap: 15px;
			padding: 10px;
		}

		.painting-item {
			grid-column: span 6 !important;
			grid-row: span 1 !important;
			height: 200px;
			border: 1px solid #ffd79a;
			background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 230, 0.9) 100%);
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.08);
		}

		.painting-tooltip {
			padding: 12px;
			background: linear-gradient(135deg, rgba(255, 249, 230, 0.95) 0%, rgba(255, 235, 205, 0.95) 100%);
		}

		.painting-tooltip h5 {
			font-size: 18px;
			color: #a0522d;
		}

		.painting-tooltip p,
		.story-intro,
		.story-details p {
			font-size: 13px;
			text-indent: 1.5em;
			color: #8b5a2b;
		}

		.story-container {
			padding: 10px;
			gap: 15px;
		}

		.story-item {
			padding: 15px;
			border: 2px solid #d4a76a;
			background: linear-gradient(135deg, #fff9e6 0%, #fff3d6 100%);
		}

		.story-header h5 {
			font-size: 16px;
			color: #a0522d;
		}

		.story-intro {
			padding: 12px;
			background: rgba(255, 255, 255, 0.6);
		}

		.story-button {
			padding: 8px 16px;
			font-size: 13px;
			background: linear-gradient(135deg, rgba(255, 240, 215, 0.9) 0%, rgba(255, 230, 180, 0.9) 100%);
			border: 1px solid #ffd79a;
			color: #8b4513;
			font-weight: 500;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.08);
			backdrop-filter: blur(8px);
		}

		.story-button:hover {
			background: linear-gradient(135deg, rgba(255, 230, 180, 0.9) 0%, rgba(255, 210, 150, 0.9) 100%);
			border-color: #ffd79a;
			color: #654321;
			box-shadow: 0 3px 8px rgba(139, 69, 19, 0.12), 0 0 6px rgba(255, 215, 0, 0.1);
		}

		.story-details {
			padding: 15px;
			background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 245, 230, 0.9) 100%);
			border: 1px solid #ffd79a;
			border-radius: 8px;
			box-shadow: 0 2px 6px rgba(139, 69, 19, 0.08);
		}
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}

		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
.navigation-bar,
.tab-bar,
.tab-content,
.paintings-section,
.story {
border-width: 3px;
}

.tab-icontent h3::after,
.paintings-section h4::after,
.story h4::after {
height: 3px;
}
}

/* 深色模式优化 */
@media (prefers-color-scheme: dark) {
body {
background-color: #3a2e21;
background-image: none;
color: #e6d7c3;
}

.navigation-bar,
.tab-bar,
.tab-content,
.paintings-section,
.story,
.story-item {
background: linear-gradient(135deg, #4a3d2e 0%, #5d4b37 50%, #4a3d2e 100%);
border-color: #a87d4a;
}

.tab-v,
.tab-icontent {
background-color: #f8f5f0;
border-color: #8b6b46;
}

.tab-icontent h3,
.paintings-section h4,
.story h4,
.story-header h5,
.painting-tooltip h5 {
color: #5d4037;
}

.tab-icontent p,
.content-details p,
.story-intro,
.story-details p,
.painting-tooltip p {
color: #5d4037;
}

.navigation-bar button,
.tab-bar button,
.story-button {
background: linear-gradient(to bottom, #8b6b46, #5d4037);
color: #f8f5f0;
border-color: #5d4037;
}

/* 小册子翻页动画 */
@keyframes pageFlip {
0% {
transform: rotateY(0deg);
opacity: 1;
}
50% {
transform: rotateY(-30deg);
opacity: 0.8;
}
100% {
transform: rotateY(0deg);
opacity: 1;
}
}

/* 灯笼晃动动画 */
@keyframes lanternSwing {
0% {
transform: rotate(-5deg);
}
50% {
transform: rotate(5deg);
}
100% {
transform: rotate(-5deg);
}
}

/* 响应式设计 - 平板设备 */
@media (max-width: 1024px) {
.booklet-container {
width: 85vw;
height: 70vh;
}

.booklet-cover,
.booklet-inner {
width: 100%;
height: 100%;
}

.left-page,
.right-page {
padding: 20px;
}

.booklet-cover h2 {
font-size: 28px;
}

.story-title {
font-size: 24px;
}

.story-introduction {
font-size: 16px;
}
}

/* 响应式设计 - 移动设备 */
@media (max-width: 768px) {
.booklet-container {
width: 95vw;
height: 80vh;
perspective: 800px;
}

/* 移动设备上简化为单页显示 */
.booklet-inner {
flex-direction: column;
}

.left-page {
width: 100%;
height: 45%;
display: flex;
align-items: center;
justify-content: center;
border-right: none;
border-bottom: 2px solid #a0522d;
}

.right-page {
width: 100%;
height: 55%;
padding: 15px;
}

.booklet-cover h2 {
font-size: 24px;
text-align: center;
}

.story-title {
font-size: 20px;
margin-bottom: 10px;
}

.story-introduction {
font-size: 14px;
line-height: 1.5;
}

/* 简化导航按钮 */
.booklet-nav {
top: 10px;
right: 10px;
flex-direction: column;
gap: 8px;
}

.prev-btn,
.next-btn {
width: 35px;
height: 35px;
font-size: 14px;
}

.page-indicator {
font-size: 12px;
}

/* 优化详情弹窗在移动设备上的显示 */
.story-details-popup {
width: 95vw;
max-height: 85vh;
padding: 15px;
}

.story-details-popup h3 {
font-size: 20px;
}

.story-details-popup p {
font-size: 14px;
}

.close-btn {
width: 30px;
height: 30px;
font-size: 16px;
}

/* 调整灯笼装饰大小 */
.lantern {
width: 40px;
height: 50px;
}

.lantern:before,
.lantern:after {
width: 40px;
height: 50px;
}
}

/* 响应式设计 - 小屏幕移动设备 */
@media (max-width: 480px) {
.booklet-container {
width: 98vw;
height: 75vh;
perspective: 600px;
}

.booklet-cover h2 {
font-size: 20px;
}

.story-title {
font-size: 18px;
}

.story-introduction {
font-size: 13px;
}

.view-details-btn {
padding: 8px 16px;
font-size: 14px;
}
}
.painting-item {
background: linear-gradient(135deg, #f8f5f0 0%, #e6d7c3 100%);
border-color: #8b6b46;
}

.painting-container {
background-color: #f8f5f0;
}

.painting-tooltip {
background: linear-gradient(135deg, rgba(93, 64, 55, 0.95) 0%, rgba(139, 107, 70, 0.95) 100%);
border-color: #5d4037;
color: #f8f5f0;
}

.painting-period {
color: #8b6b46;
}