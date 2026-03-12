import React, { useState, useMemo } from "react";
import styles from "./ContactPage.module.css";
import { Search, Phone, Mail, Building2, UserCircle } from "lucide-react";

// 직급별 우선순위 (수치가 낮을수록 상단에 배치)
const ROLE_PRIORITY: { [key: string]: number } = {
  대표: 1,
  CTO: 2,
  팀장: 3,
  파트장: 4,
  팀원: 5,
};

const CONTACT_DATA = [
  // 경영진
  {
    id: 1,
    name: "박수범",
    team: "경영총괄",
    role: "대표",
    email: "subum.park@smartwork.com",
    phone: "010-1000-0001",
  },

  // 기술팀 - 기술팀장(CTO)
  {
    id: 2,
    name: "고용재",
    team: "기술팀",
    role: "CTO",
    email: "yongjae.ko@smartwork.com",
    phone: "010-2000-0001",
  },

  // 기술팀 - 인프라 파트
  {
    id: 3,
    name: "윤준영",
    team: "기술팀 (인프라)",
    role: "파트장",
    email: "junyoung.yoon@smartwork.com",
    phone: "010-2001-0001",
  },
  {
    id: 4,
    name: "신수연",
    team: "기술팀 (인프라)",
    role: "팀원",
    email: "suyeon.shin@smartwork.com",
    phone: "010-2001-0002",
  },

  // 기술팀 - 개발 파트
  {
    id: 5,
    name: "김준협",
    team: "기술팀 (개발)",
    role: "파트장",
    email: "junhyeop.kim@smartwork.com",
    phone: "010-2002-0001",
  },
  {
    id: 6,
    name: "강유정",
    team: "기술팀 (개발)",
    role: "팀원",
    email: "yujeong.kang@smartwork.com",
    phone: "010-2002-0002",
  },

  // 인사팀
  {
    id: 7,
    name: "이정우",
    team: "인사팀",
    role: "팀장",
    email: "jungwoo.lee@smartwork.com",
    phone: "010-3000-0001",
  },
  {
    id: 8,
    name: "조현수",
    team: "인사팀",
    role: "팀원",
    email: "hyunsoo.cho@smartwork.com",
    phone: "010-3000-0002",
  },
];

const ContactPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const groupedContacts = useMemo(() => {
    // 1. 검색 필터링
    const filtered = CONTACT_DATA.filter(
      (c) =>
        c.name.includes(searchTerm) ||
        c.team.includes(searchTerm) ||
        c.role.includes(searchTerm),
    );

    // 2. 부서별 그룹화
    const groups: { [key: string]: typeof CONTACT_DATA } = {};
    filtered.forEach((contact) => {
      if (!groups[contact.team]) groups[contact.team] = [];
      groups[contact.team].push(contact);
    });

    // 3. 부서 정렬 (경영총괄이 항상 맨 위, 나머지는 가나다) 및 직급 정렬
    const sortedGroupKeys = Object.keys(groups).sort((a, b) => {
      if (a === "경영총괄") return -1;
      if (b === "경영총괄") return 1;
      return a.localeCompare(b, "ko");
    });

    return sortedGroupKeys.map((teamName) => ({
      teamName,
      members: groups[teamName].sort(
        (a, b) => (ROLE_PRIORITY[a.role] || 99) - (ROLE_PRIORITY[b.role] || 99),
      ),
    }));
  }, [searchTerm]);

  return (
    <div className={styles.container}>
      <header className={styles.headerSection}>
        <div className={styles.titleGroup}>
          <h1 className={styles.title}>임직원 연락처</h1>
          <p className={styles.subtitle}>부서별 조직도 및 연락처 현황</p>
        </div>
        <div className={styles.searchWrapper}>
          <Search className={styles.searchIcon} size={18} />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="이름 또는 부서 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </header>

      {/* 가변형 그리드 엔진 */}
      <div className={styles.teamsMasonryGrid}>
        {groupedContacts.map((group) => (
          <section key={group.teamName} className={styles.teamSection}>
            <div className={styles.teamHeader}>
              <div className={styles.teamInfo}>
                <Building2 size={18} className={styles.teamIcon} />
                <h2 className={styles.teamTitle}>{group.teamName}</h2>
              </div>
              <span className={styles.memberCount}>{group.members.length}</span>
            </div>

            <div className={styles.memberList}>
              {group.members.map((member) => (
                <div key={member.id} className={styles.memberItem}>
                  <div className={styles.memberTop}>
                    <UserCircle size={32} className={styles.avatar} />
                    <div className={styles.nameBox}>
                      <span className={styles.memberName}>{member.name}</span>
                      <span className={styles.memberRole}>{member.role}</span>
                    </div>
                  </div>
                  <div className={styles.memberDetails}>
                    <div className={styles.detailRow}>
                      <Phone size={12} /> <span>{member.phone}</span>
                    </div>
                    <div className={styles.detailRow}>
                      <Mail size={12} />{" "}
                      <span>{member.email.split("@")[0]}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>

      {groupedContacts.length === 0 && (
        <div className={styles.noResult}>검색 결과가 없습니다.</div>
      )}
    </div>
  );
};

export default ContactPage;
