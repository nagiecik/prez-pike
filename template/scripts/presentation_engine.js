// Silnik interaktywny prezentacji CHOPIN
document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    const totalSlides = slides.length;
    let currentSlide = 0;
    let currentSubStep = 0;

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const overlayPrevBtn = document.getElementById('overlayPrevBtn');
    const overlayNextBtn = document.getElementById('overlayNextBtn');
    const slideCounter = document.getElementById('slideCounter');
    const progressBar = document.getElementById('progressBar');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    const overviewBtn = document.getElementById('overviewBtn');
    const overviewOverlay = document.getElementById('overviewOverlay');
    const closeOverviewBtn = document.getElementById('closeOverviewBtn');
    const overviewGrid = document.getElementById('overviewGrid');

    // Przełączanie Motywu Jasny/Ciemny
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');

    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-theme');
            themeIcon.className = 'fa-solid fa-moon';
            themeToggleBtn.title = 'Przełącz na motyw Ciemny (T)';
        } else {
            document.body.classList.remove('light-theme');
            themeIcon.className = 'fa-solid fa-sun';
            themeToggleBtn.title = 'Przełącz na motyw Jasny (T)';
        }
        localStorage.setItem('presentation_theme', theme);
    }

    function toggleTheme() {
        const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    }

    const savedTheme = localStorage.getItem('presentation_theme') || 'dark';
    applyTheme(savedTheme);

    themeToggleBtn.addEventListener('click', toggleTheme);

    const slideCompleted = {};

    function getSubStepElements(slideIndex) {
        const slide = slides[slideIndex];
        if (!slide) return [];

        const caseFlow = slide.querySelector('.case-study-flow');
        if (caseFlow) {
            const caseItems = slide.querySelectorAll('.case-step-card, .case-summary-trigger');
            if (caseItems.length > 0) return Array.from(caseItems);
        }

        const mSteps = slide.querySelectorAll('#slide2Cascade .m-step');
        if (mSteps.length > 0) return Array.from(mSteps);

        const featureBullets = slide.querySelectorAll('.feature-list li');
        if (featureBullets.length > 0) return Array.from(featureBullets);

        const tiles = slide.querySelectorAll('.tiled-content .tile');
        if (tiles.length > 0) return Array.from(tiles);

        const layers = slide.querySelectorAll('.layer-card');
        if (layers.length > 0) return Array.from(layers);

        const stackedCards = slide.querySelectorAll('.stacked-card');
        if (stackedCards.length > 0) return Array.from(stackedCards);

        const caseSteps = slide.querySelectorAll('.case-step-card');
        if (caseSteps.length > 0) return Array.from(caseSteps);

        return [];
    }

    function updateSubSteps() {
        const elements = getSubStepElements(currentSlide);
        if (elements.length === 0) return;

        const isCaseStudy = slides[currentSlide].querySelector('.case-study-flow');
        if (isCaseStudy) {
            const slideEl = slides[currentSlide];
            const track = slideEl.querySelector('#caseVTrack');
            const totalSteps = 6;
            const current = Math.min(Math.max(currentSubStep, 1), totalSteps);

            // Kroki 1 do 5: Pionowy przesuw i wyostrzenie TYLKO 1 kafelka naraz
            if (current <= 5) {
                slideEl.classList.remove('mode-overview');
                const stepIdx = current - 1; // 0..4
                const cardHeightWithGap = 340;
                const vShift = -stepIdx * cardHeightWithGap;

                if (track) {
                    track.style.transform = `translateY(${vShift}px)`;
                }

                elements.forEach((el, idx) => {
                    const stepNum = idx + 1;
                    el.classList.remove('tile-active', 'tile-normal', 'tile-dimmed', 'tile-passed');
                    if (stepNum === current) {
                        el.classList.add('tile-active');
                    } else if (stepNum < current) {
                        el.classList.add('tile-passed');
                    } else {
                        el.classList.add('tile-dimmed');
                    }
                });
            } else {
                // Krok 6: Tryb pełnego podsumowania (wszystkie kafelki w 1 rzędzie + podsumowanie)
                slideEl.classList.add('mode-overview');
                if (track) {
                    track.style.transform = 'none';
                }
                elements.forEach((el) => {
                    el.classList.remove('tile-dimmed', 'tile-active', 'tile-passed');
                    el.classList.add('tile-normal');
                });
            }
            // Aktualizacja bocznego wskaźnika postępu (case-indicator-dot)
            const indicatorDots = slideEl.querySelectorAll('.case-indicator-dot');
            indicatorDots.forEach((dot) => {
                const stepNum = parseInt(dot.getAttribute('data-step'), 10);
                if (stepNum === current) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
            return;
        }

        const isCascade = slides[currentSlide].querySelector('#slide2Cascade');
        const isBullets = slides[currentSlide].querySelector('.feature-list');
        const isTiles = slides[currentSlide].querySelector('.tiled-content, .ecosystem-layers, .stacked-cards-container, .concentric-nested-wrapper, .concentric-ecosystem-slide');

        elements.forEach((el, idx) => {
            const stepNum = idx + 1;
            el.classList.remove('step-active', 'step-normal', 'bullet-active', 'bullet-normal', 'bullet-dimmed', 'tile-active', 'tile-normal', 'tile-dimmed');

            if (isCascade) {
                if (stepNum === currentSubStep) {
                    el.classList.add('step-active');
                } else if (stepNum < currentSubStep) {
                    el.classList.add('step-normal');
                }
            } else if (isBullets) {
                if (stepNum === currentSubStep) {
                    el.classList.add('bullet-active');
                } else if (stepNum < currentSubStep) {
                    el.classList.add('bullet-normal');
                } else {
                    el.classList.add('bullet-dimmed');
                }
            } else if (isTiles) {
                if (stepNum === currentSubStep) {
                    el.classList.add('tile-active');
                } else if (stepNum < currentSubStep) {
                    el.classList.add('tile-normal');
                } else {
                    el.classList.add('tile-dimmed');
                }
            }
        });
    }

    // Kliknięcie bezpośrednio w kafelek / bullet / dot
    slides.forEach((slide, sIdx) => {
        const elements = getSubStepElements(sIdx);
        elements.forEach((el, eIdx) => {
            el.addEventListener('click', (e) => {
                if (e) e.stopPropagation();
                if (currentSlide === sIdx) {
                    currentSubStep = eIdx + 1;
                    updateSubSteps();
                }
            });
        });

        const dots = slide.querySelectorAll('.case-dot-node, .case-indicator-dot');
        dots.forEach((dot) => {
            dot.addEventListener('click', (e) => {
                if (e) e.stopPropagation();
                if (currentSlide === sIdx) {
                    const stepAttr = dot.getAttribute('data-step');
                    if (stepAttr) {
                        currentSubStep = parseInt(stepAttr, 10);
                    }
                    updateSubSteps();
                }
            });
        });
    });


    let autoLoopInterval = null;

    function stopAutoLoop() {
        if (autoLoopInterval) {
            clearInterval(autoLoopInterval);
            autoLoopInterval = null;
        }
    }

    function startAutoLoop(slideIndex) {
        stopAutoLoop();
        const slide = slides[slideIndex];
        if (!slide || !slide.hasAttribute('data-auto-loop')) return;

        const subStepElements = getSubStepElements(slideIndex);
        if (subStepElements.length === 0) return;

        // Wyzerowanie: każde wejście na slajd zaczyna animację od pętli od początku (krok 1)
        currentSubStep = 1;
        updateSubSteps();

        autoLoopInterval = setInterval(() => {
            if (currentSlide !== slideIndex) {
                stopAutoLoop();
                return;
            }
            const elements = getSubStepElements(slideIndex);
            if (elements.length > 0) {
                currentSubStep = (currentSubStep % elements.length) + 1;
                updateSubSteps();
            }
        }, 1300);
    }

    function getSlideFromHash() {
        const hash = window.location.hash.replace('#', '');
        const num = parseInt(hash, 10);
        if (!isNaN(num) && num >= 1 && num <= totalSlides) {
            return num - 1;
        }
        return 0;
    }

    function goToSlide(index, fromPrev = true) {
        stopAutoLoop();

        if (index < 0) index = 0;
        if (index >= totalSlides) index = totalSlides - 1;

        slides.forEach((slide, idx) => {
            if (idx === index) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });

        currentSlide = index;

        const subStepElements = getSubStepElements(currentSlide);
        if (subStepElements.length > 0) {
            // Zasada globalna: Pierwszy element jest zawsze domyślnie aktywny (highlight) na start
            const startAttr = slides[currentSlide].getAttribute('data-start-step');
            currentSubStep = startAttr ? parseInt(startAttr, 10) : 1;
            updateSubSteps();
        }

        if (slides[currentSlide] && slides[currentSlide].hasAttribute('data-auto-loop')) {
            startAutoLoop(currentSlide);
        }

        slideCounter.textContent = `${currentSlide + 1} / ${totalSlides}`;
        
        const progress = ((currentSlide + 1) / totalSlides) * 100;
        progressBar.style.width = `${progress}%`;

        history.replaceState(null, null, `#${currentSlide + 1}`);
        updateOverviewCards();
    }

    function nextSlide() {
        const currentSlideEl = slides[currentSlide];
        if (currentSlideEl && currentSlideEl.hasAttribute('data-auto-loop')) {
            if (currentSlide < totalSlides - 1) {
                goToSlide(currentSlide + 1, true);
            }
            return;
        }

        const subStepElements = getSubStepElements(currentSlide);
        if (subStepElements.length > 0 && currentSubStep < subStepElements.length) {
            currentSubStep++;
            updateSubSteps();
            return;
        }

        if (currentSlide < totalSlides - 1) {
            goToSlide(currentSlide + 1, true);
        }
    }

    function prevSlide() {
        const currentSlideEl = slides[currentSlide];
        if (currentSlideEl && currentSlideEl.hasAttribute('data-auto-loop')) {
            if (currentSlide > 0) {
                goToSlide(currentSlide - 1, false);
            }
            return;
        }

        const subStepElements = getSubStepElements(currentSlide);
        if (subStepElements.length > 0 && currentSubStep > 1) {
            currentSubStep--;
            updateSubSteps();
            return;
        }

        if (currentSlide > 0) {
            goToSlide(currentSlide - 1, false);
        }
    }

    const overviewTitlesMap = [
        "Ekosystem Nowoczesnego Operatora",
        "Wzrost Bez Rozrostu Kosztów",
        "Łańcuch Obciążenia Operacyjnego",
        "Odpowiedź Na Wyzwania Skalowania",
        "Samoobsługa Klienta W eBOK",
        "Redukcja Rutyny W BOK",
        "Podgląd Aplikacji Abonenta",
        "Automatyzacja Procesów Back-Office",
        "Pełny Widok Klienta 360°",
        "Pulpit Nawigacyjny Operatora",
        "Mobilny Cyfrowy Technik",
        "Błyskawiczne Realizacje Zleceń",
        "Podgląd Aplikacji Technika",
        "Transparentny Status Zlecenia",
        "Status Zlecenia Na Żywo",
        "Podgląd Postępu Realizacji",
        "Jedna Platforma Dla Spółek",
        "Zwinna Absorpcja Nowych Podmiotów",
        "Wspólny Ekosystem 5 Spółek",
        "Ekosystem Zamiast Sztywnego Monolitu",
        "3 Warstwy Ekosystemu Operacyjnego",
        "Dwie Perspektywy Wspólnej Wartości",
        "Proces End-to-End W Praktyce",
        "Gotowość Na Bezpieczne Skalowanie",
        "Podsumowanie Oraz Pytania Q&A"
    ];

    function initOverview() {
        overviewGrid.innerHTML = '';
        slides.forEach((slide, idx) => {
            const card = document.createElement('div');
            card.className = `overview-card ${idx === currentSlide ? 'current' : ''}`;
            card.dataset.index = idx;

            let titleText = slide.getAttribute('data-overview-title') || overviewTitlesMap[idx];
            if (!titleText) {
                const heading = slide.querySelector('h1, h2');
                if (heading) {
                    titleText = heading.textContent.replace(/\s+/g, ' ').trim();
                    if (titleText.length > 50) {
                        titleText = titleText.substring(0, 50) + '...';
                    }
                } else {
                    titleText = `Slajd ${idx + 1}`;
                }
            }

            card.innerHTML = `
                <div class="overview-card-num">SLAJD ${idx + 1}</div>
                <div class="overview-card-title">${titleText}</div>
            `;

            card.addEventListener('click', () => {
                goToSlide(idx);
                toggleOverview(false);
            });

            overviewGrid.appendChild(card);
        });
    }

    function updateOverviewCards() {
        const cards = overviewGrid.querySelectorAll('.overview-card');
        cards.forEach((card, idx) => {
            if (idx === currentSlide) {
                card.classList.add('current');
            } else {
                card.classList.remove('current');
            }
        });
    }

    function toggleOverview(show) {
        if (show === undefined) {
            overviewOverlay.classList.toggle('active');
        } else if (show) {
            overviewOverlay.classList.add('active');
        } else {
            overviewOverlay.classList.remove('active');
        }
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.warn(`Błąd pełnego ekranu: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);
    overlayPrevBtn.addEventListener('click', prevSlide);
    overlayNextBtn.addEventListener('click', nextSlide);
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    overviewBtn.addEventListener('click', () => toggleOverview(true));
    closeOverviewBtn.addEventListener('click', () => toggleOverview(false));

    // Modal Komentarzy (Netlify Forms)
    const commentBtn = document.getElementById('commentBtn');
    const commentOverlay = document.getElementById('commentOverlay');
    const closeCommentBtn = document.getElementById('closeCommentBtn');
    const cancelCommentBtn = document.getElementById('cancelCommentBtn');
    const commentForm = document.getElementById('commentForm');
    const commentSlideBadge = document.getElementById('commentSlideBadge');
    const commentSlideInput = document.getElementById('commentSlideInput');
    const commentSlideTitleInput = document.getElementById('commentSlideTitleInput');
    const commentSuccessMsg = document.getElementById('commentSuccessMsg');
    const closeSuccessBtn = document.getElementById('closeSuccessBtn');
    const successSlideRef = document.getElementById('successSlideRef');

    function getSlideTitle(slideIndex) {
        const slide = slides[slideIndex];
        if (!slide) return `Slajd ${slideIndex + 1}`;
        const heading = slide.querySelector('h1, h2, .slide-title, .title');
        return heading ? heading.innerText.trim().replace(/\n+/g, ' ') : `Slajd ${slideIndex + 1}`;
    }

    function toggleCommentModal(open) {
        if (!commentOverlay) return;
        const shouldOpen = open !== undefined ? open : !commentOverlay.classList.contains('active');
        if (shouldOpen) {
            const slideNum = currentSlide + 1;
            const slideTitle = getSlideTitle(currentSlide);
            if (commentSlideBadge) commentSlideBadge.innerText = `Slajd #${slideNum}`;
            if (commentSlideInput) commentSlideInput.value = slideNum;
            if (commentSlideTitleInput) commentSlideTitleInput.value = slideTitle;
            if (successSlideRef) successSlideRef.innerText = `Slajdu #${slideNum}`;

            if (commentForm) {
                commentForm.reset();
                commentForm.style.display = 'flex';
            }
            if (commentSuccessMsg) commentSuccessMsg.style.display = 'none';

            commentOverlay.classList.add('active');
            const commentText = document.getElementById('commentText');
            if (commentText) setTimeout(() => commentText.focus(), 100);
        } else {
            commentOverlay.classList.remove('active');
        }
    }

    if (commentBtn) commentBtn.addEventListener('click', () => toggleCommentModal(true));
    if (closeCommentBtn) closeCommentBtn.addEventListener('click', () => toggleCommentModal(false));
    if (cancelCommentBtn) cancelCommentBtn.addEventListener('click', () => toggleCommentModal(false));
    if (closeSuccessBtn) closeSuccessBtn.addEventListener('click', () => toggleCommentModal(false));
    if (commentOverlay) {
        commentOverlay.addEventListener('click', (e) => {
            if (e.target === commentOverlay) toggleCommentModal(false);
        });
    }

    if (commentForm) {
        commentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(commentForm);
            const submitBtn = document.getElementById('submitCommentBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Wysyłanie...';
            }

            const isLocal = window.location.protocol === 'file:' || 
                            window.location.hostname === 'localhost' || 
                            window.location.hostname === '127.0.0.1';

            if (isLocal) {
                setTimeout(() => {
                    if (commentForm) commentForm.style.display = 'none';
                    if (commentSuccessMsg) {
                        commentSuccessMsg.style.display = 'flex';
                        let note = commentSuccessMsg.querySelector('.local-demo-note');
                        if (!note) {
                            note = document.createElement('p');
                            note.className = 'local-demo-note';
                            note.style.cssText = 'font-size: 0.82rem; color: #eab308; margin-top: 8px; font-style: italic; background: rgba(234, 179, 8, 0.1); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(234, 179, 8, 0.2);';
                            note.innerText = '💡 Tryb podglądu lokalnego: Po opublikowaniu na Netlify ten komentarz trafi na Twój e-mail.';
                            commentSuccessMsg.appendChild(note);
                        }
                    }
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Wyślij uwagę';
                    }
                }, 400);
                return;
            }

            const bodyData = new URLSearchParams(formData);
            if (!bodyData.get('form-name')) {
                bodyData.set('form-name', 'presentation-comments');
            }

            fetch('/', {
                method: 'POST',
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: bodyData.toString()
            })
            .then((res) => {
                if (res.ok || res.status < 400) {
                    if (commentForm) commentForm.style.display = 'none';
                    if (commentSuccessMsg) {
                        const note = commentSuccessMsg.querySelector('.local-demo-note');
                        if (note) note.remove();
                        commentSuccessMsg.style.display = 'flex';
                    }
                } else {
                    console.error('Błąd odpowiedzi Netlify:', res.status);
                    alert('Błąd serwera Netlify (' + res.status + '). Upewnij się, że wgrałeś aktualną wersję z ukrytym formularzem.');
                }
            })
            .catch((err) => {
                console.error('Błąd wysyłania komentarza:', err);
                alert('Błąd sieci podczas wysyłania komentarza. Spróbuj ponownie.');
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Wyślij uwagę';
                }
            });
        });
    }

    document.addEventListener('keydown', (e) => {
        if (commentOverlay && commentOverlay.classList.contains('active')) {
            if (e.key === 'Escape') {
                toggleCommentModal(false);
            }
            return;
        }

        if (overviewOverlay.classList.contains('active')) {
            if (e.key === 'Escape' || e.key === 'o' || e.key === 'O') {
                toggleOverview(false);
            }
            return;
        }

        if (document.activeElement && (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA')) {
            return;
        }

        switch (e.key) {
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
            case 'PageDown':
            case 'Enter':
                e.preventDefault();
                nextSlide();
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
            case 'Backspace':
                e.preventDefault();
                prevSlide();
                break;
            case 'Home':
                e.preventDefault();
                goToSlide(0);
                break;
            case 'End':
                e.preventDefault();
                goToSlide(totalSlides - 1);
                break;
            case 'f':
            case 'F':
                toggleFullscreen();
                break;
            case 'o':
            case 'O':
                toggleOverview(true);
                break;
            case 't':
            case 'T':
                toggleTheme();
                break;
            case 'c':
            case 'C':
                toggleCommentModal(true);
                break;
        }
    });

    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const diff = touchEndX - touchStartX;
        if (Math.abs(diff) > 50) {
            if (diff < 0) {
                nextSlide();
            } else {
                prevSlide();
            }
        }
    }

    initOverview();
    goToSlide(getSlideFromHash());

    window.addEventListener('hashchange', () => {
        goToSlide(getSlideFromHash());
    });

    // Automatyczne odświeżanie przeglądarki (Live Reload) tylko na lokalnym serwerze (localhost / 127.0.0.1)
    (function setupLiveReload() {
        const isLocalHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        if (!isLocalHost) return;

        let initialTimestamp = null;
        const initialMatch = document.documentElement.outerHTML.match(/<!-- BUILD_TIMESTAMP:\s*(\d+(\.\d+)?) -->/);
        if (initialMatch) {
            initialTimestamp = initialMatch[1];
        }

        setInterval(() => {
            fetch(window.location.href, { cache: 'no-store' })
                .then(res => res.text())
                .then(html => {
                    const newMatch = html.match(/<!-- BUILD_TIMESTAMP:\s*(\d+(\.\d+)?) -->/);
                    if (newMatch && initialTimestamp && newMatch[1] !== initialTimestamp) {
                        console.log('[LiveReload] Wykryto nową kompilację prezentacji. Odświeżam stronę...');
                        window.location.reload();
                    }
                })
                .catch(() => {});
        }, 1500);
    })();
});

