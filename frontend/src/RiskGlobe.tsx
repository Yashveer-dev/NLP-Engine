import React, { useEffect, useRef } from "react";
import * as THREE from "three";

interface RiskGlobeProps {
  impactScore?: number;
  sentiment?: number;
}

export const RiskGlobe: React.FC<RiskGlobeProps> = ({ impactScore = 8, sentiment = -0.65 }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 210;

    // Renderer (transparent, lightweight, antialiased)
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Group for easy tilt and rotation
    const globeGroup = new THREE.Group();
    globeGroup.rotation.x = 0.25;
    scene.add(globeGroup);

    // Dynamic accent color based on impact and sentiment
    const isHighRisk = impactScore >= 7;
    const baseColor = isHighRisk ? 0xef4444 : sentiment >= 0 ? 0x10b981 : 0x38bdf8;
    const coreColor = isHighRisk ? 0xf43f5e : 0x0284c7;

    // 1. Icosahedron Wireframe Core
    const sphereGeo = new THREE.IcosahedronGeometry(72, 3);
    const wireMat = new THREE.MeshBasicMaterial({
      color: baseColor,
      wireframe: true,
      transparent: true,
      opacity: 0.18,
    });
    const wireMesh = new THREE.Mesh(sphereGeo, wireMat);
    globeGroup.add(wireMesh);

    // 2. Inner Glow Mesh
    const innerGeo = new THREE.IcosahedronGeometry(68, 2);
    const innerMat = new THREE.MeshBasicMaterial({
      color: coreColor,
      wireframe: true,
      transparent: true,
      opacity: 0.08,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    globeGroup.add(innerMesh);

    // 3. Orbital Particles / Points
    const particleCount = 280;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const radius = 72;

    for (let i = 0; i < particleCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;

      positions[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = radius * Math.cos(phi);
    }

    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 2.2,
      color: 0xffffff,
      transparent: true,
      opacity: 0.85,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    globeGroup.add(particleSystem);

    // 4. Concentric Orbital Rings (Equatorial and Angled)
    const ringGeo1 = new THREE.RingGeometry(86, 87.2, 64);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: baseColor,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35,
    });
    const ringMesh1 = new THREE.Mesh(ringGeo1, ringMat1);
    ringMesh1.rotation.x = Math.PI / 2.3;
    globeGroup.add(ringMesh1);

    const ringGeo2 = new THREE.RingGeometry(94, 94.8, 64);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.15,
    });
    const ringMesh2 = new THREE.Mesh(ringGeo2, ringMat2);
    ringMesh2.rotation.x = Math.PI / 1.7;
    ringMesh2.rotation.y = 0.4;
    globeGroup.add(ringMesh2);

    // Mouse tracking for subtle interactive parallax
    let mouseX = 0;
    let mouseY = 0;
    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      mouseX = x * 0.4;
      mouseY = y * 0.4;
    };
    window.addEventListener("mousemove", onMouseMove);

    // Animation Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      // Smooth constant rotation
      globeGroup.rotation.y += 0.0035;
      ringMesh1.rotation.z += 0.002;
      ringMesh2.rotation.z -= 0.003;

      // Mouse interactive lerp
      globeGroup.rotation.x += (mouseY + 0.25 - globeGroup.rotation.x) * 0.05;
      globeGroup.position.x += (mouseX * 25 - globeGroup.position.x) * 0.05;

      renderer.render(scene, camera);
    };
    animate();

    // Resize Handler
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [impactScore, sentiment]);

  return <div ref={containerRef} className="w-full h-full min-h-[380px] relative pointer-events-none" />;
};
